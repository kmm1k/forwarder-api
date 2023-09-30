import logging
import time

import requests

loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BetSite:
    def __init__(self):
        self.session = requests.Session()
        self.last_used_username = None
        self.last_used_password = None
        self.last_login_url = None
        logger.info("BetSite init")

    def login(self, username, password, url):
        logger.info("BetSite login")
        self.last_used_username = username
        self.last_used_password = password
        self.last_login_url = url
        payload = {
            'username': username,
            'password': password
        }

        response = self.session.post(url, data=payload)

        if response.status_code == 200:
            if "Username" in response.text:
                logger.error("Login failed, received the login page as a response.")
                return False
            return True
        return False

    def get_bets_data(self, url):
        MAX_RETRIES = 3
        RETRY_DELAY = 5  # delay between retries, in seconds

        logger.info(f"BetSite get_bets_data from url {url}")

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url)

                if self.is_session_expired(response):
                    logger.warning("Session expired. Trying to re-login.")
                    if self.login(self.last_used_username, self.last_used_password, self.last_login_url):
                        logger.info("Re-login successful. Retrying the request.")
                        response = self.session.get(url)
                    else:
                        logger.error("Re-login failed.")
                        return None

                # Log the full response for debugging
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {response.headers}")
                logger.debug(f"Response content: {response.text}")

                if response.status_code == 200:
                    try:
                        return response.json()
                    except requests.exceptions.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from response. Content: {response.text}")
                        return None

            except requests.exceptions.ConnectionError:
                if attempt < MAX_RETRIES - 1:  # No need to sleep on the last attempt
                    logger.warning(f"Connection error. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("Max retries reached. Could not get data.")
                    return None

    def is_session_expired(self, response):
        # Assuming session expiration is detected by the presence of "Username" in response text
        # Adjust this method based on your exact criteria
        return "Username" in response.text
