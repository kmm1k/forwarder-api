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


if __name__ == '__main__':
    config = open_creds()

    username = config['corners_username']
    password = config['corners_password']
    login_url = config['corners_login_url']

    chat_sing_id = config['chat_sing_id']

    corner_betsite = BetSite()
    corner_betsite.login(username, password, login_url)

    corners_sing_api_url = config['corners_sing_api_url']
    corners_sing_bets = corner_betsite.get_bets_data(corners_sing_api_url)
    logger.info(corners_sing_bets)

