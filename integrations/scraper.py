import asyncio
import json
import logging
import os
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
        self.dashboard_v2_site = BetSite()
        # we should update this every time we get new data, to prevent memory leaks
        self.bets_dict = {}
        # has to be a dict, because we have 2 urls and data sources
        self.last_updated = {}
        self.placed_bets = {}
        self.clean_delay_queue = {}
        self.clean_message_count = 0
        self.bet365_last_updated = time.time()

    def start(self):
        with open('./integrations/creds.yml', 'rb') as f:
            config = yaml.safe_load(f)
        self.login_to_dashboard_v2(config)
        asyncio.run(self.periodic_task(config))

    def login_to_dashboard_v2(self, config):
        username = config['get_data2_username']
        password = config['get_data2_password']
        login_url = config['get_data2_login_url']
        if self.dashboard_v2_site.login(username, password, login_url):
            logger.info("Logged in successfully to dashboard_v2_site bet site!")
        else:
            logger.info("Failed to log in to dashboard_v2_site bet site.")

    async def periodic_task(self, config):
        while True:
            message_queues = await self.get_and_parse_data(config)
            await self.send_data_to_bot(message_queues, config)
            await asyncio.sleep(30)

    async def get_and_parse_data(self, config):
        # now all of the data comes from the same site
        # api now returns a field called dashboard_name, which we can use to separate the messages
        # dashboard_name can be 'sing' or 'bet365'

        message_queues = {"sing": [], "bet365": [], "bet365_clean": []}

        # Fetch data from the new unified API endpoint
        unified_api_url = config['get_data2_api_url']
        unified_data_with_metadata = self.dashboard_v2_site.get_bets_data(unified_api_url)
        if unified_data_with_metadata is None:
            logger.error("Failed to fetch data from the unified API endpoint.")
            return message_queues

        unified_data = json.loads(unified_data_with_metadata['data'])

        sing_data = []
        bet365_data = []
        # Process the data based on 'dashboard_name'
        for bet_line in unified_data:
            dashboard_name = bet_line.get('dashboard_name', '').lower()
            if dashboard_name == 'sing':
                sing_data.append(bet_line)

            if dashboard_name == 'bet365':
                bet365_data.append(bet_line)

        # ORIGINAL SING SITE SCRAPING
        # logger.info(f"sing elements in list: {len(sing_data)}")
        new_bets = self.get_new_bets("sing_bets", sing_data)
        sing_message_queue = self.process_new_bets(new_bets, "Sing")
        message_queues["sing"] = sing_message_queue

        # ORIGINAL BET365 SITE SCRAPING
        # logger.info(f"bet365 elements in list: {len(bet365_data)}")
        new_bets = self.get_new_bets("bet365_bets", bet365_data)
        bet365_message_queue = self.process_new_bets(new_bets, "Bet365")
        message_queues["bet365"] = bet365_message_queue

        # SPECIAL BET365 SITE SCRAPING (1 second delay)
        bet365_clean_new_bets = self.get_new_bets_based_on_uuid("bet365_clean", bet365_data)
        bet365_message_queue = self.process_new_bets_clean(bet365_clean_new_bets, "Bet365")
        message_queues["bet365_clean"] = bet365_message_queue

        # clean bets that are older than 1 hour for bet365_clean
        current_time = time.time()
        if current_time - self.bet365_last_updated >= 1 * 60 * 60:
            self.bet365_last_updated = current_time
            self.bets_dict["bet365_clean"] = {}

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

        # Check the delay queue and send messages older than 1 second
        for message, message_time in list(self.clean_delay_queue.items()):
            if current_time - message_time >= 1:  # 1 seconds
                payload = {
                    'chat_id': config['chat_bet365_clean_id'],
                    'text': message,
                    'parse_mode': 'MarkdownV2'
                }
                # check if clean_message_count.txt has a number or if clean_message_count is > 0, then send a message
                self.clean_message_count = self.get_clean_message_count()
                if self.clean_message_count > 0:
                    self.clean_message_count = self.clean_message_count - 1
                    response = requests.post(telegram_url, data=payload)
                    if self.clean_message_count == 0:
                        end_payload = {
                            'chat_id': config['chat_bet365_clean_id'],
                            'text': 'All messages sent\n',
                            'parse_mode': 'MarkdownV2'
                        }
                        requests.post(telegram_url, data=end_payload)
                # Remove the message from the queue after sending
                del self.clean_delay_queue[message]

    def get_clean_message_count(self):
        if self.clean_message_count <= 0:
            try:
                with open('./clean_message_count.txt', 'r') as f:
                    clean_message_count = int(f.read())
            except Exception as e:
                clean_message_count = 0
            finally:
                # delete file if exists
                try:
                    os.remove('./clean_message_count.txt')
                except Exception as e:
                    pass
        else:
            clean_message_count = self.clean_message_count
        return clean_message_count

    def check_bet_for_placed_and_add_to_dict(self, bet):
        if bet['placed_count'] > 0:
            if bet['uuid'] not in self.placed_bets:
                self.placed_bets[bet['uuid']] = bet
                # logger.info(f"Placed bet: {bet['uuid']}")

    def get_new_bets(self, url, data):
        new_bets = []

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

        parsed_bets = {}
        for item in data:
            parsed_bets[item['uuid']] = item

        if url not in self.bets_dict:
            self.bets_dict[url] = parsed_bets
            old_parsed_bets = self.bets_dict[url]
        else:
            old_parsed_bets = self.bets_dict[url]
            for key, value in parsed_bets.items():
                if key not in old_parsed_bets:
                    new_bets.append(value)

        # append to the dict
        old_parsed_bets.update(parsed_bets)
        self.bets_dict[url] = old_parsed_bets
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
