import asyncio
import logging

import yaml

from telethon import TelegramClient, events
from telethon.events import NewMessage

loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


class Relay:
    bot_name = "bot"
    channel_pairs = []

    def _save_config(self, config):
        with open('./integrations/relay_creds.yml', 'w') as f:
            yaml.safe_dump(config, f)

    async def start(self, config):
        self.channel_pairs = config["channel_pairs"]
        self.bot_name = config["bot_name"]
        bot = TelegramClient(config["bot_name"],
                             config["api_id"],
                             config["api_hash"])
        await bot.start(bot_token=config["bot_token"])
        logger.info("loaded configs and starting relay")

        adding_pattern = f'\/awadd.+'
        remove_pattern = f'\/awremove.+'
        list_pattern = f'\/awlist'
        help_pattern = f'\/help'
        exclude_commands = ['/awlist', '/awadd', '/awremove', '/help']

        @bot.on(events.NewMessage())
        async def handler(event: NewMessage.Event):
            if any(event.message.message.startswith(cmd) for cmd in exclude_commands):
                return
            await from_to_forwarding(event)

        async def from_to_forwarding(event):
            for i in self.channel_pairs:
                if i[0] == event.chat_id:
                    target_id = i[1]
                    file = await bot.download_media(event.message.media)
                    await bot.send_message(target_id, event.message.message, file=file)
                elif i[1] == event.chat_id:
                    target_id = i[0]
                    file = await bot.download_media(event.message.media)
                    await bot.send_message(target_id, event.message.message, file=file)

        @bot.on(events.NewMessage(pattern=list_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            if str(event.to_id.user_id) in config["bot_token"]:
                await bot.send_message(event.chat_id, f'config channel pairs {config["channel_pairs"]}')

        @bot.on(events.NewMessage(pattern=adding_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            if str(event.to_id.user_id) in config["bot_token"]:
                request = event.text.replace(f'/awadd ', "")
                request = request.replace(',', "")
                request = request.replace('g', "-")
                ids = request.split(" ")
                source = int(ids[0])
                target = int(ids[1])
                config["channel_pairs"].append([source, target])
                self._save_config(config)
                self.channel_pairs = config["channel_pairs"]
                await bot.send_message(event.chat_id, f'added chat id\'s input: {source}, output: {target}')
                await bot.send_message(event.chat_id, f'config channel pairs {config["channel_pairs"]}')

        @bot.on(events.NewMessage(pattern=remove_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            if str(event.to_id.user_id) in config["bot_token"]:
                request = event.text.replace(f'/awremove ', "")
                request = request.replace(',', "")
                request = request.replace('g', "-")
                ids = request.split(" ")
                source = int(ids[0])
                target = int(ids[1])
                config["channel_pairs"].remove([source, target])
                self._save_config(config)
                self.channel_pairs = config["channel_pairs"]
                await bot.send_message(event.chat_id, f'removed chat id\'s input: {source}, output: {target}')
                await bot.send_message(event.chat_id, f'config channel pairs {config["channel_pairs"]}')

        @bot.on(events.NewMessage(pattern=help_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            await bot.send_message(event.chat_id, f'this bot contains forwarder: \n'
                                                  f'/awlist - displays all the forwarded chats [chat_A, chat_B] \n'
                                                  f'/awadd [chat_A_id], [chat_B_id] - add a forward \n'
                                                  f'example: /awadd -123456789, -987654321 \n'
                                                  f'/awremove [chat_A_id], [chat_B_id] - remove forward \n'
                                                  f'example: /awremove -123456789, -987654321 \n')

        await bot.run_until_disconnected()

    def init(self):
        with open('./integrations/relay_creds.yml', 'rb') as f:
            config = yaml.safe_load(f)
        asyncio.run(self.start(config))
