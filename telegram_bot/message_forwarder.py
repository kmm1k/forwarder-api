import asyncio
import logging
import time

import yaml
from asgiref.sync import sync_to_async
from telethon import TelegramClient, events
from telethon.events import NewMessage

loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


class MessageForwarder:
    bot_name = "bot"

    async def start(self, config):
        from bot.models import Forwarding
        from bot.models import TagGroups

        self.bot_name = config["bot_name"]
        bot = TelegramClient(config["bot_name"],
                             config["api_id"],
                             config["api_hash"])
        await bot.start(bot_token=config["bot_token"])
        logger.info("loaded configs and starting")

        at_bot_pattern = f'(?i)@{self.bot_name}.+'
        at_tag_pattern = f'(?i)@.+'

        @bot.on(events.NewMessage(pattern=at_tag_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            tagGroups = await sync_to_async(list)(TagGroups.objects.all().filter(tag=event.text))

            for i in tagGroups:
                logger.info(f"tagging {i.tag} with {i.usernames}")
                usernames = i.usernames.split(',')
                output = ""
                for k in usernames:
                    output += f'{k.strip()} '
                await bot.send_message(int(event.chat_id), output)

        @bot.on(events.NewMessage(pattern=at_bot_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            await from_to_forwarding(event)
            await to_from_forwarding(event)

        async def from_to_forwarding(event):
            forwardings = await sync_to_async(list)(Forwarding.objects.all().filter(from_chat=event.chat_id))
            for i in forwardings:
                logger.info(f"forwarded {i.from_chat} to {i.to_chats}")
                await bot.send_message(event.chat_id, 'Booked!')
                to_chats = i.to_chats.split(',')
                for i in to_chats:
                    await bot.forward_messages(int(i.strip()), event.id, int(event.chat_id))

        async def to_from_forwarding(event):
            forwardings = await sync_to_async(list)(Forwarding.objects.all().filter(to_chats__contains=event.chat_id))
            for i in forwardings:
                logger.info(f"forwarded {i.from_chat} to {i.to_chats}")
                await bot.send_message(event.chat_id, 'Sending something back!')
                await bot.forward_messages(int(i.from_chat.strip()), event.id, event.chat_id)

        await bot.run_until_disconnected()

    def startDef(self):
        with open('./telegram_bot/config.yml', 'rb') as f:
            config = yaml.safe_load(f)
        asyncio.run(self.start(config))
