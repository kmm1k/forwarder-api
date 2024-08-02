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

    async def start(self, config):
        self.channel_pairs = config["channel_pairs"]
        self.bot_name = config["bot_name"]
        bot = TelegramClient(config["bot_name"],
                             config["api_id"],
                             config["api_hash"])
        await bot.start(bot_token=config["bot_token"])
        logger.info("loaded configs and starting relay")

        # make it work without a pattern

        @bot.on(events.NewMessage())
        async def handler(event: NewMessage.Event):
            await from_to_forwarding(event)

        async def from_to_forwarding(event):
            for i in self.channel_pairs:
                if i[0] == event.chat_id:
                    target_id = i[1]
                    file = await bot.download_media(event.message.media)
                    await bot.send_message(target_id, event.message.message, file=file)

        await bot.run_until_disconnected()

    def init(self):
        with open('./integrations/relay_creds.yml', 'rb') as f:
            config = yaml.safe_load(f)
        asyncio.run(self.start(config))
