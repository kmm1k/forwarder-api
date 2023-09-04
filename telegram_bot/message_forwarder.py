import asyncio
import logging

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
        from bot.models import TagForwarding

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
            await tag_grouper(event)
            await tag_forwarding(event)

        async def tag_forwarding(event):
            first_word = event.text.split(' ')[0]
            tag_forwardings = await sync_to_async(list)(TagForwarding.objects.all().filter(tag=first_word))
            for i in tag_forwardings:
                to_chats = i.to_chats
                to_chats = [chat.strip() for chat in to_chats]
                allowed_users = i.allowed_users
                allowed_users = [user.strip() for user in allowed_users]
                logger.info(f"allowed users are {allowed_users}")
                logger.info(f"event sender id is {event.sender_id}")
                for k in to_chats:
                    logger.info(f"trying to forward {i.tag} to {k}, event chatId is {event.chat_id}")
                    if ((str(event.sender_id) in allowed_users or len(allowed_users) == 0)
                            and int(k.strip()) != int(event.chat_id)):
                        file = await bot.download_media(event.message.media, file=bytes)
                        event.message.message = event.message.message.replace(first_word, '', 1)
                        await bot.send_message(int(k.strip()), event.message.message, file=file)

        async def tag_grouper(event):
            tag_groups = await sync_to_async(list)(TagGroups.objects.all().filter(tag=event.text))
            for i in tag_groups:
                logger.info(f"tagging {i.tag} with {i.usernames}")
                usernames = i.usernames
                usernames = [user.strip() for user in usernames]
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
                to_chats = i.to_chats
                to_chats = [str(chat).strip() for chat in to_chats]
                for i in to_chats:
                    await bot.forward_messages(int(i.strip()), event.id, int(event.chat_id))

        async def to_from_forwarding(event):
            all_forwardings = await sync_to_async(list)(Forwarding.objects.all())
            forwardings = []
            for i in all_forwardings:
                to_chats = i.to_chats
                to_chats = [str(chat).strip() for chat in to_chats]
                if str(event.chat_id) in to_chats:
                    forwardings.append(i)
            for i in forwardings:
                logger.info(f"forwarded {i.from_chat} to {i.to_chats}")
                await bot.send_message(event.chat_id, 'Message sent back')
                await bot.forward_messages(int(i.from_chat.strip()), event.id, event.chat_id)

        await bot.run_until_disconnected()

    def startDef(self):
        with open('./telegram_bot/config.yml', 'rb') as f:
            config = yaml.safe_load(f)
        asyncio.run(self.start(config))
