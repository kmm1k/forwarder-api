import asyncio
import json
import logging
from datetime import datetime

import yaml

from integrations.client.bet_site import BetSite
from integrations.print_model import PrintModel
from integrations.scraper import Scraper

loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


# This file is a playground for testing manually and has alot of commented code,
# because it is easier to use that way
def open_creds():
    with open('./creds.yml', 'rb') as f:
        return yaml.safe_load(f)


def login():
    pass
    # betsSite.login(username, password, login_url)
    # if betsSite.login(username, password, login_url):
    #     logger.info("Logged in successfully!")
    # else:
    #     logger.info("Failed to log in.")


if __name__ == '__main__':
    # betsSite = BetSite()
    config = open_creds()
    # username = config['username']
    # password = config['password']
    # login_url = config['login_url']
    chat_sing_id = config['chat_sing_id']
    chat_bet365_id = config['chat_bet365_id']
    #
    # login()
    #
    # sing_api_url = config['sing_api_url']
    # sing_bets = betsSite.get_bets_data(sing_api_url)
    # logger.info(sing_bets)
    #
    # timestamp = sing_bets['mtime']
    # last_updated = datetime.utcfromtimestamp(timestamp)
    # logger.info(last_updated)
    #
    bets_dict = {}
    with open('./test_data.json', 'rb') as f:
        res = json.loads(f.read())

    # this is response from the endpoint
    # we need to parse this to the correct format
    encased_data_field = res['data']
    data_json = json.loads(encased_data_field)
    logger.info(data_json)
    data_json = data_json[0:1]
    message_queues = {}
    for bet in data_json:
        model = PrintModel(
            page_name="sing",
            hours_to_start=bet['hours_to_start'],
            league=bet['league'],
            home_team=bet['home_team'],
            away_team=bet['away_team'],
            bet_type=bet['bet_type'],
            mod=bet['mod'],
            price=bet['price'],
            bet_class=bet['bet_class']
        )
        print(model.get_markdown())
        message_queues["sing"] = [model.get_markdown()]
    scraper = Scraper()
    asyncio.run(scraper.send_data_to_bot(message_queues, config))
