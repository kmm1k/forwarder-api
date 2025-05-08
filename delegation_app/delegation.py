from __future__ import annotations

"""
Delegation Workflow Bot — _v2.0_
================================
*Integrated, test‑friendly reminder engine*

Key additions
-------------
• **JobQueue‑based reminders** – run daily (default 09:00 local) **and** on‑demand via `/remind [days]`.
• No more separate `--remind` CLI mode; reminders are part of normal bot runtime.
• Easy local testing: `/remind 0` pings immediate‑due tasks so you don't wait.

(Everything else from the original v1.0 is retained.)
"""

import datetime as _dt
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

import yaml  # PyYAML

try:
    import gspread
except ImportError as exc:  # pragma: no cover – helpful hint
    sys.exit("\n[!] Missing Google client libraries. Install with: pip install gspread google-auth\n")

try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
        JobQueue,
        CallbackContext,
    )
    from telegram.helpers import escape_markdown
except ImportError:  # pragma: no cover
    sys.exit("\n[!] python-telegram-bot v20+ is required. Install with: pip install python-telegram-bot --pre\n")

############################################################
# Configuration helpers
############################################################

CONFIG_PATH = Path("config.yml")
EXPECTED_YAML_KEYS = {
    "bot_token",
    "spreadsheet_id",
    "sheet_id",
}

REMINDER_DAYS_DEFAULT = 2  # "due in ≤X days" threshold
REMINDER_HOUR_LOCAL = 9  # daily reminder time (09:00 local timezone)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)5s] %(name)s: %(message)s")


def load_config(path: Path = CONFIG_PATH) -> dict:
    if not path.exists():
        logger.error("Config file %s not found", path)
        sys.exit(1)
    with path.open() as f:
        cfg = yaml.safe_load(f)
    missing = EXPECTED_YAML_KEYS - cfg.keys()
    if missing:
        logger.error("Config missing keys: %s", ", ".join(sorted(missing)))
        sys.exit(1)
    return cfg


############################################################
# Google Sheets backend
############################################################

def get_gspread_client(cfg: dict) -> gspread.Client:
    cred_path = cfg.get("service_account_json") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        logger.error(
            "Google service‑account credentials not provided. Set GOOGLE_APPLICATION_CREDENTIALS or service_account_json."
        )
        sys.exit(1)
    return gspread.service_account(filename=cred_path)


def open_worksheet(client: gspread.Client, cfg: dict):
    ss = client.open_by_key(cfg["spreadsheet_id"])
    ws = ss.get_worksheet(int(cfg["sheet_id"]))
    return ws


def _next_task_id(ws) -> str:
    """Return the next task code like TSK004."""
    ids = [row[0] for row in ws.get_all_values() if row]
    if len(ids) <= 1:  # header only
        return "TSK001"
    last = ids[-1]
    match = re.search(r"TSK(\d+)", last)
    num = int(match.group(1)) if match else len(ids)
    return f"TSK{num + 1:03d}"


def add_task(ws, assignee: str, description: str, deadline: str, chat_id: int) -> str:
    task_id = _next_task_id(ws)
    ws.append_row(
        [task_id, assignee, description, deadline, "Pending", str(chat_id), 0],
        value_input_option="USER_ENTERED",
    )
    return task_id


def _update_progress(ws, numeric_id: str, percent: int, user_tag: str) -> Tuple[bool, str]:
    task_id = f"TSK{int(numeric_id):03d}"
    rows = ws.get_all_values()
    for idx, row in enumerate(rows, start=1):
        if row and row[0] == task_id:
            if row[1] != user_tag:
                return False, "unauthorized"
            # write percentage
            ws.update_cell(idx, 7, percent)  # col G
            if percent == 100 and row[4] != "Done":
                ws.update_cell(idx, 5, "Done")  # col E
            if percent != 100 and row[4] != "Pending":
                ws.update_cell(idx, 5, "Pending")
            return True, task_id
    return False, "not_found"


def due_within(ws, days: int) -> List[Tuple[str, str, str, int]]:
    today = _dt.date.today()
    upcoming: List[Tuple[str, str, str, int]] = []
    for row in ws.get_all_values()[1:]:
        if not row or row[4] != "Pending":
            continue
        deadline = _dt.date.fromisoformat(row[3])
        delta = (deadline - today).days
        if 0 <= delta <= days:
            upcoming.append((row[0], row[1], row[3], int(row[5])))
    return upcoming


############################################################
# Reminder helpers (async) — shared by Job & /remind cmd
############################################################

async def _send_reminders(bot, ws, days: int) -> int:
    """Return number of reminder messages sent."""
    count = 0
    for task_id, assignee, deadline, chat_id in due_within(ws, days):
        msg = (
            f"⏰ Reminder: {task_id} assigned to {assignee} is due {deadline}. "
            f"Reply /done {task_id[-3:]} when finished."
        )
        try:
            await bot.send_message(chat_id=chat_id, text=msg)
            count += 1
        except Exception as e:  # pragma: no cover – network errors etc.
            logger.warning("Failed to send reminder to chat %s: %s", chat_id, e)
    return count


async def reminder_job(context: CallbackContext):
    days = context.job.data.get("days", REMINDER_DAYS_DEFAULT)
    ws = context.application.bot_data["ws"]
    await _send_reminders(context.bot, ws, days)


############################################################
# Telegram bot handlers
############################################################

ASSIGN_RE = re.compile(r"/assign\s+(?P<users>[^;]+);(?P<desc>[^;]+);\s?(?P<date>\d{4}-\d{2}-\d{2})", re.I)
DONE_RE = re.compile(r"/done\s+(?P<num>\d{3})(?:\s+(?P<pct>\d{1,3})%?)?", re.I)


async def assign_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = update.message.text or ""
    match = ASSIGN_RE.search(text)
    if not match:
        return

    ws = context.bot_data["ws"]
    users_raw = match.group("users").strip()
    description = match.group("desc").strip()
    deadline = match.group("date")

    assignees: List[str] = []
    for part in users_raw.split("+"):
        tag = part.strip()
        if not tag:
            continue
        if not tag.startswith("@"):
            tag = f"@{tag}"
        assignees.append(tag)

    if not assignees:
        await update.message.reply_text("⚠️ No valid usernames provided after /assign.")
        return

    created: List[Tuple[str, str]] = []  # (task_id, assignee)
    for assignee in assignees:
        task_id = add_task(ws, assignee, description, deadline, update.effective_chat.id)
        created.append((task_id, assignee))

    # Build feedback message
    if len(created) == 1:
        task_id, assignee = created[0]
        await update.message.reply_text(f"✅ {task_id} assigned to {assignee}, due {deadline}.")
    else:
        lines = [f"✅ Created {len(created)} tasks (due {deadline}):"]
        for task_id, assignee in created:
            lines.append(f"• {task_id} → {assignee}")
        await update.message.reply_text("\n".join(lines))


async def done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = update.message.text or ""
    match = DONE_RE.search(text)
    if not match:
        return

    username = update.effective_user.username
    if not username:
        await update.message.reply_text("You need a Telegram @username set to mark tasks done.")
        return
    user_tag = f"@{username}"

    pct_raw = match.group('pct')
    try:
        percent = 100 if pct_raw is None else int(pct_raw)
    except ValueError:
        await update.message.reply_text("Percentage must be 0–100.")
        return
    if not 0 <= percent <= 100:
        await update.message.reply_text("Percentage must be between 0 and 100.")
        return

    ws = context.bot_data["ws"]
    ok, info = _update_progress(ws, match.group('num'), percent, user_tag)

    if not ok:
        if info == "unauthorized":
            await update.message.reply_text("⚠️ Only the assignee can update this task.")
        else:  # not_found
            await update.message.reply_text("⚠️ Task not found. Check the number and try again.")
        return

    if percent == 100:
        await update.message.reply_text(f"✅ {info} marked complete. Great job!")
    else:
        await update.message.reply_text(f"📈 {info} updated to {percent}%. Keep going!")


async def remind_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual trigger: /remind [days] (defaults to REMINDER_DAYS_DEFAULT)."""
    days = REMINDER_DAYS_DEFAULT
    if context.args:
        try:
            days = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Days must be an integer number ≥0.")
            return
    ws = context.bot_data["ws"]
    sent = await _send_reminders(context.bot, ws, days)
    await update.message.reply_text(f"📣 Sent {sent} reminder(s) for tasks due within {days} day(s).")


def _collect_tasks(
        ws,
        assignee_tag: str,
        include_done: bool = False,
) -> List[Tuple[str, str, str, str]]:
    rows = ws.get_all_values()[1:]
    tasks = []
    for row in rows:
        if not row:
            continue
        task_id, assignee, desc, deadline, status, chat_id, *rest = row
        pct = int(rest[0]) if rest else 0
        if assignee != assignee_tag:
            continue
        if not include_done and status != "Pending":
            continue
        tasks.append((task_id, desc, deadline, status, pct))
    return tasks


def _format_tasks(task_rows: List[Tuple[str, str, str, str, int]]) -> str:
    if not task_rows:
        return "🎉 Good job\\! You have no more tasks\\! 🏖️"

    lines = []
    for task_id, desc, dl, status, pct in task_rows:
        safe_desc = escape_markdown(desc, version=2)
        safe_dl = escape_markdown(dl, version=2)
        safe_status = escape_markdown(status, version=2)
        safe_pct = escape_markdown(str(pct), version=2)
        lines.append(
            f"• `{task_id}` – {safe_desc} \\(due {safe_dl}, {safe_status}, {safe_pct}%\\)"
        )
    return "\n".join(lines)


async def list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply with *pending* tasks assigned to the caller."""
    if not update.message:
        return
    username = update.effective_user.username
    if not username:
        await update.message.reply_text(
            "You don’t appear to have a Telegram @username set, "
            "so I can’t match tasks to you\\."
        )
        return
    ws = context.bot_data["ws"]
    tasks = _collect_tasks(ws, f"@{username}", include_done=False)
    await update.message.reply_markdown_v2(_format_tasks(tasks))


async def list_all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply with *all* tasks (Pending + Done) assigned to the caller."""
    if not update.message:
        return
    username = update.effective_user.username
    if not username:
        await update.message.reply_text(
            "You don’t appear to have a Telegram @username set, "
            "so I can’t match tasks to you\\."
        )
        return
    ws = context.bot_data["ws"]
    tasks = _collect_tasks(ws, f"@{username}", include_done=True)
    await update.message.reply_markdown_v2(_format_tasks(tasks))


HELP_TEXT = """\
*Delegation Workflow Bot — Commands*

• `/assign @user;Task description;YYYY\\-MM\\-DD`
  \\- Create a new task \\(TSK\\#\\#\\#\\) for @user, due on the given date\\.
  
• `/assign @user1+@user2;Task description;YYYY\\-MM\\-DD`
  \\- Create a new task \\(TSK\\#\\#\\#\\) for multiple users
  \\- @user1 and @user2 and so on \\.

• `/done NNN`
  \\- Mark task *TSKNNN* complete \\(e\\.g\\. /done 005\\)\\.

• `/done NNN percentage%`
  \\- Mark task *TSKNNN* partially complete \\(e\\.g\\. /done 005 50%\\)\\.

• `/list`
  \\- Show all pending tasks assigned to you\\.
  
• `/listall`
  \\- Show all tasks assigned to you, even done tasks\\.

• `/help`
  \\- Show this message\\.
"""


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(
        HELP_TEXT,
        disable_web_page_preview=True,
    )


############################################################
# Entry point (no CLI — one script, one job queue)
############################################################

def main():
    cfg = load_config()

    # GSpread
    gc = get_gspread_client(cfg)
    ws = open_worksheet(gc, cfg)

    # Telegram application
    application = Application.builder().token(cfg["bot_token"]).build()

    # Share cfg + worksheet among handlers
    application.bot_data["cfg"] = cfg
    application.bot_data["ws"] = ws

    # JobQueue: daily reminders
    hour = REMINDER_HOUR_LOCAL
    job_queue: JobQueue = application.job_queue
    job_queue.run_daily(
        reminder_job,
        time=_dt.time(hour=hour, tzinfo=_dt.timezone.utc).replace(tzinfo=None),  # naive local time
        name="daily‑reminder",
        data={"days": REMINDER_DAYS_DEFAULT},
    )
    # Also run once at startup so you can test immediately after launching
    job_queue.run_once(reminder_job, when=0, name="startup‑reminder", data={"days": REMINDER_DAYS_DEFAULT})

    # Slash‑command handlers
    application.add_handler(CommandHandler("assign", assign_handler))
    application.add_handler(CommandHandler("done", done_handler))
    application.add_handler(CommandHandler("remind", remind_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("list", list_handler))
    application.add_handler(CommandHandler("listall", list_all_handler))

    # Mention (@bot assign...) support (chats)
    mention_assign = filters.TEXT & filters.Regex(re.compile(rf"@{cfg['bot_name']}\s+assign", re.I))
    mention_done = filters.TEXT & filters.Regex(re.compile(rf"@{cfg['bot_name']}\s+done", re.I))

    application.add_handler(MessageHandler(mention_assign, assign_handler))
    application.add_handler(MessageHandler(mention_done, done_handler))

    logger.info("Bot started as %s (reminders: daily %02d:00, threshold ≤%dd)", cfg["bot_name"], hour,
                REMINDER_DAYS_DEFAULT)
    application.run_polling()


if __name__ == "__main__":
    main()
