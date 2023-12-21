import asyncio
import json
import logging
import time

import requests
import yaml

from integrations.client.bet_site import BetSite
from integrations.print_model import PrintModel
from integrations.helpers.hash_calculator import compute_bet_model_hash

loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self):
        self.betsSite = BetSite()
        self.cornersSite = BetSite()
        # we should update this every time we get new data, to prevent memory leaks
        self.bets_dict = {}
        # has to be a dict, because we have 2 urls and data sources
        self.last_updated = {}
        self.placed_bets = {}
        self.clean_delay_queue = {}

    def start(self):
        with open('./integrations/creds.yml', 'rb') as f:
            config = yaml.safe_load(f)
        self.login(config)
        self.login_to_corners(config)
        asyncio.run(self.periodic_task(config))

    def login(self, config):
        username = config['username']
        password = config['password']
        login_url = config['login_url']
        if self.betsSite.login(username, password, login_url):
            logger.info("Logged in successfully to main bet site!")
        else:
            logger.info("Failed to log in to main bet site.")

    def login_to_corners(self, config):
        username = config['corners_username']
        password = config['corners_password']
        login_url = config['corners_login_url']
        if self.cornersSite.login(username, password, login_url):
            logger.info("Logged in successfully to corners bet site!")
        else:
            logger.info("Failed to log in to corners bet site.")

    async def periodic_task(self, config):
        while True:
            message_queues = await self.get_and_parse_data(config)
            await self.send_data_to_bot(message_queues, config)
            await asyncio.sleep(30)

    async def get_and_parse_data(self, config):
        # message queue saves messages from both urls,
        # we need to separate those, and send message to the correct chat
        message_queues = {}

        # ORIGINAL SING SITE SCRAPING
        chat_sing_api_url = config['sing_api_url']
        sing_data = self.betsSite.get_bets_data(chat_sing_api_url)
        # logger.info(f"sing elements in list: {len(json.loads(sing_data['data']))}")
        new_bets = self.get_new_bets(chat_sing_api_url, sing_data['data'])
        sing_message_queue = self.process_new_bets(new_bets, "Sing")
        message_queues["sing"] = sing_message_queue

        # ORIGINAL BET365 SITE SCRAPING
        chat_bet365_api_url = config['bet365_api_url']
        bet365_data = self.betsSite.get_bets_data(chat_bet365_api_url)
        # logger.info(f"bet365 elements in list: {len(json.loads(bet365_data['data']))}")
        new_bets = self.get_new_bets(chat_bet365_api_url, bet365_data['data'])
        bet365_message_queue = self.process_new_bets(new_bets, "Bet365")
        message_queues["bet365"] = bet365_message_queue

        # SPECIAL BET365 SITE SCRAPING (5 minute delay)
        bet365_clean_new_bets = self.get_new_bets_based_on_uuid("bet365_clean", bet365_data['data'])
        bet365_message_queue = self.process_new_bets_clean(bet365_clean_new_bets, "Bet365")
        message_queues["bet365_clean"] = bet365_message_queue

        # CORNERS SING SITE SCRAPING
        corners_sing_api_url = config['corners_sing_api_url']
        corners_sing_data = self.cornersSite.get_bets_data(corners_sing_api_url)
        logger.info(f"corners_sing elements in list: {len(json.loads(corners_sing_data['data']))}")
        new_bets = self.get_new_bets(corners_sing_api_url, corners_sing_data['data'])
        corners_sing_message_queue = self.process_new_bets(new_bets, "Corners Sing")
        message_queues["sing"] += corners_sing_message_queue

        return message_queues

    async def send_data_to_bot(self, message_queues, config):
        telegram_url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
        current_time = time.time()

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
                # logger.info(response.text)

        if "bet365" in message_queues:
            message_queue = message_queues["bet365"]
            for message in message_queue:
                payload = {
                    'chat_id': config['chat_bet365_id'],
                    'text': message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(telegram_url, data=payload)
                # logger.info(response.text)

        # Handle 'bet365_clean' queue with a delay
        if "bet365_clean" in message_queues:
            for message in message_queues["bet365_clean"]:
                # Add each message to the delay queue with its own timestamp
                self.clean_delay_queue[message] = current_time

        # Check the delay queue and send messages older than 5 minutes
        for message, message_time in list(self.clean_delay_queue.items()):
            if current_time - message_time >= 300:  # 5 minutes
                payload = {
                    'chat_id': config['chat_bet365_clean_id'],
                    'text': message,
                    'parse_mode': 'MarkdownV2'
                }
                response = requests.post(telegram_url, data=payload)
                # Remove the message from the queue after sending
                del self.clean_delay_queue[message]

    def check_bet_for_placed_and_add_to_dict(self, bet):
        if bet['placed_count'] > 0:
            if bet['uuid'] not in self.placed_bets:
                self.placed_bets[bet['uuid']] = bet
                # logger.info(f"Placed bet: {bet['uuid']}")

    def get_new_bets(self, url, data):
        new_bets = []
        data = json.loads(data)

        parsed_bets = {}
        for item in data:
            item_hash = compute_bet_model_hash(item)
            parsed_bets[item_hash] = item
            self.check_bet_for_placed_and_add_to_dict(item)

        if url not in self.bets_dict:
            self.bets_dict[url] = parsed_bets
        else:
            old_parsed_bets = self.bets_dict[url]
            for key, value in parsed_bets.items():
                if key not in old_parsed_bets:
                    new_bets.append(value)

        self.bets_dict[url] = parsed_bets
        return new_bets

    def get_new_bets_based_on_uuid(self, url, data):
        new_bets = []
        data = json.loads(data)

        parsed_bets = {}
        for item in data:
            parsed_bets[item['uuid']] = item

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
                bet_class=bet['bet_class'],
                placed_count=bet['placed_count'],
                placed_price=self.get_placed_price(bet['uuid'])
            )
            formatted_bets.append(model.get_markdown())
        return formatted_bets

    def process_new_bets_clean(self, new_bets, page_name):
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
                bet_class=bet['bet_class'],
                placed_count=0,
                placed_price="No Price"
            )
            formatted_bets.append(model.get_markdown())
        return formatted_bets

    def get_placed_price(self, uuid):
        if uuid in self.placed_bets:
            return str(self.placed_bets[uuid]['price'])
        return "Not placed yet"

