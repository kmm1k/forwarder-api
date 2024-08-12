import asyncio
import logging
import os

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
        from bot.models import ChatsWithBot

        self.bot_name = config["bot_name"]
        bot = TelegramClient(config["bot_name"],
                             config["api_id"],
                             config["api_hash"])
        await bot.start(bot_token=config["bot_token"])
        logger.info("loaded configs and starting")

        at_bot_pattern = f'(?i)@{self.bot_name}.+'
        at_tag_pattern = f'(?i)@.+'
        at_tag_grouper_pattern = f'(?i).*@\w+( |$)'
        slash_start_pattern = f'(?i)/start\s*[0-9]+'

        @bot.on(events.ChatAction())
        async def handler(event):
            # Check if the bot has been added to the chat
            added = event.user_added or event.created or event.user_joined
            me = await bot.get_me()
            if added and event.user_id == me.id:
                await create_chat_record(event.chat_id, event.chat.title)

        @sync_to_async
        def create_chat_record(chat_id, title):
            try:
                ChatsWithBot.objects.create(chat_id=chat_id, name=title)
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    pass
                logger.info(e)

        @bot.on(events.NewMessage(pattern=at_tag_grouper_pattern))
        async def handler(event: NewMessage.Event):
            await tag_grouper(event)

        @bot.on(events.NewMessage(pattern=slash_start_pattern))
        async def handler(event: NewMessage.Event):
            # check if chat where command is run is in the config under clean_chat_id
            if str(event.chat_id) != str(config['clean_chat_id']):
                return
            # get the number from the message
            number = event.text.split(' ')[1]
            # save the number to file in clean_message_count.txt
            await write_to_file(number)
            await bot.send_message(event.chat_id, f'Waiting for {number} messages to send.')

        async def write_to_file(number):
            if number == 0 or number == '' or number == '0':
                return
            # deleting the file and writing to it
            try:
                os.remove('./clean_message_count.txt')
            except Exception as e:
                pass

            try:
                with open('./clean_message_count.txt', 'w') as f:
                    f.write(str(number))
            except Exception as e:
                pass

        @bot.on(events.NewMessage(pattern=at_tag_pattern))
        async def handler(event: NewMessage.Event):
            await tag_forwarding(event)

        async def tag_forwarding(event):
            first_word = event.text.split(' ')[0]
            tag_forwardings = await sync_to_async(list)(TagForwarding.objects.all().filter(tag=first_word))
            for i in tag_forwardings:
                to_chats = i.to_chats
                to_chats = [chat.strip() for chat in to_chats]
                allowed_users = i.allowed_users
                allowed_users = [user.strip() for user in allowed_users]
                for k in to_chats:
                    if ((str(event.sender_id) in allowed_users or len(allowed_users) == 0)
                            and int(k.strip()) != int(event.chat_id)):
                        file = await bot.download_media(event.message.media, file=bytes)
                        event.message.message = event.message.message.replace(first_word, '', 1)
                        await bot.send_message(int(k.strip()), event.message.message, file=file)

        async def tag_grouper(event):
            tag_groups = await sync_to_async(list)(TagGroups.objects.all())
            # see if any tag is in the message
            # and filter out the tags_groups that are in the message
            tag_groups = [i for i in tag_groups if i.tag in event.message.message]
            for i in tag_groups:
                usernames = i.usernames
                usernames = [user.strip() for user in usernames]
                output = ""
                for k in usernames:
                    output += f'{k.strip()} '
                await bot.send_message(int(event.chat_id), output)

        @bot.on(events.NewMessage(pattern=at_bot_pattern))
        async def handler(event: NewMessage.Event):
            await from_to_forwarding(event)
            await to_from_forwarding(event)

        async def from_to_forwarding(event):
            forwardings = await sync_to_async(list)(Forwarding.objects.all().filter(from_chat=event.chat_id))
            for i in forwardings:
                await bot.send_message(event.chat_id, 'Booked!')
                to_chats = i.to_chats
                to_chats = [str(chat).strip() for chat in to_chats]
                for i in to_chats:
                    if event.reply_to_msg_id:
                        await bot.forward_messages(int(i.strip()), event.reply_to_msg_id, int(event.chat_id))
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
                if event.reply_to_msg_id:
                    await bot.forward_messages(int(i.from_chat.strip()), event.reply_to_msg_id, event.chat_id)
                await bot.forward_messages(int(i.from_chat.strip()), event.id, event.chat_id)
                await bot.send_message(event.chat_id, 'Message sent back')

        await bot.run_until_disconnected()

    def startDef(self):
        with open('./telegram_bot/config.yml', 'rb') as f:
            config = yaml.safe_load(f)
        asyncio.run(self.start(config))
