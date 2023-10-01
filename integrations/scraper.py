import asyncio
import json
import logging

import requests
import yaml

from integrations.client.bet_site import BetSite
from integrations.print_model import PrintModel
from integrations.tests.helpers.hash_calculator import compute_bet_model_hash

loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self):
        self.betsSite = BetSite()
        # we should update this every time we get new data, to prevent memory leaks
        self.bets_dict = {}
        # has to be a dict, because we have 2 urls and data sources
        self.last_updated = {}

    def start(self):
        with open('./integrations/creds.yml', 'rb') as f:
            config = yaml.safe_load(f)
        self.login(config)
        asyncio.run(self.periodic_task(config))

    def login(self, config):
        username = config['username']
        password = config['password']
        login_url = config['login_url']
        if self.betsSite.login(username, password, login_url):
            logger.info("Logged in successfully!")
        else:
            logger.info("Failed to log in.")

    async def periodic_task(self, config):
        while True:
            message_queues = await self.get_and_parse_data(config)
            await self.send_data_to_bot(message_queues, config)
            await asyncio.sleep(30)

    async def get_and_parse_data(self, config):
        # message queue saves messages from both urls,
        # we need to separate those, and send message to the correct chat
        message_queues = {}

        chat_sing_api_url = config['sing_api_url']
        sing_data = self.betsSite.get_bets_data(chat_sing_api_url)
        logger.info(f"sing elements in list: {len(json.loads(sing_data['data']))}")
        new_bets = self.get_new_bets(chat_sing_api_url, sing_data['data'])
        sing_message_queue = self.process_new_bets(new_bets, "Sing")
        message_queues["sing"] = sing_message_queue

        chat_bet365_api_url = config['bet365_api_url']
        bet365_data = self.betsSite.get_bets_data(chat_bet365_api_url)
        logger.info(f"bet365 elements in list: {len(json.loads(bet365_data['data']))}")
        new_bets = self.get_new_bets(chat_bet365_api_url, bet365_data['data'])
        bet365_message_queue = self.process_new_bets(new_bets, "Bet365")
        message_queues["bet365"] = bet365_message_queue

        return message_queues

    async def send_data_to_bot(self, message_queues, config):
        telegram_url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"

        if not message_queues:
            return

        if "sing" in message_queues:
            message_queue = message_queues["sing"]
            for message in message_queue:
                payload = {
                    'chat_id': config['chat_sing_id'],
                    'text': message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(telegram_url, data=payload)
                logger.info(response.text)

        if "bet365" in message_queues:
            message_queue = message_queues["bet365"]
            for message in message_queue:
                payload = {
                    'chat_id': config['chat_bet365_id'],
                    'text': message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(telegram_url, data=payload)
                logger.info(response.text)

    def get_new_bets(self, url, data):
        new_bets = []
        data = json.loads(data)

        parsed_bets = {}
        for item in data:
            item_hash = compute_bet_model_hash(item)
            parsed_bets[item_hash] = item

        if url not in self.bets_dict:
            self.bets_dict[url] = parsed_bets
        else:
            old_parsed_bets = self.bets_dict[url]
            for key, value in parsed_bets.items():
                if key not in old_parsed_bets:
                    new_bets.append(value)

        self.bets_dict[url] = parsed_bets
        return new_bets

    def process_new_bets(self, new_bets, page_name):
        formatted_bets = []
        for bet in new_bets:
            model = PrintModel(
                page_name=page_name,
                hours_to_start=bet['hours_to_start'],
                league=bet['league'],
                home_team=bet['home_team'],
                away_team=bet['away_team'],
                bet_type=bet['bet_type'],
                mod=bet['mod'],
                price=bet['price'],
                bet_class=bet['bet_class']
            )
            formatted_bets.append(model.get_markdown())
        return formatted_bets
