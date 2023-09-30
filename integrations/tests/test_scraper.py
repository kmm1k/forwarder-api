import asyncio
import json
import unittest
from unittest.mock import patch, MagicMock

from integrations.client.bet_site import BetSite
from integrations.scraper import Scraper


class TestScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()

    @patch("builtins.open", new_callable=MagicMock)
    @patch("yaml.safe_load")
    @patch("asyncio.run")
    @patch("requests.Session.post")  # Mock the post method
    @patch("requests.Session.get")  # Mock the get method
    def test_start(self, mock_get, mock_post, mock_run, mock_safe_load, mock_open):
        # Create a fake response object to be returned by mocked post/get method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Some text that doesn't contain 'Username'"
        mock_response.json.return_value = {}

        mock_post.return_value = mock_response
        mock_get.return_value = mock_response

        mock_safe_load.return_value = {
            "username": "testuser",
            "password": "testpassword",
            "login_url": "https://testloginurl.com",
        }
        self.scraper.start()

        mock_open.assert_called_once_with('./integrations/creds.yml', 'rb')
        self.assertTrue(mock_safe_load.called)
        self.assertTrue(mock_run.called)

    @patch("requests.post")
    def test_send_data_to_bot(self, mock_post):
        mock_post.return_value.text = "Mock Response"
        config = {
            "bot_token": "test_token",
            "chat_sing_id": "test_chat_id",
            "chat_bet365_id": "test_chat_id",
        }
        message_queues = {
            "sing": ["Test Message 1", "Test Message 2"],
            "bet365": ["Test Message 3"]
        }

        asyncio.run(self.scraper.send_data_to_bot(message_queues, config))
        self.assertEqual(mock_post.call_count, 3)

    @patch("builtins.open", new_callable=MagicMock)
    @patch("yaml.safe_load")
    @patch("asyncio.run")
    @patch("requests.Session.post")
    @patch("requests.Session.get")
    @patch.object(BetSite, "get_bets_data")
    def test_no_bets_on_start(self, mock_get_bets_data, mock_get, mock_post, mock_run, mock_safe_load, mock_open):
        # Given when there is no bets_dict
        # When starting the scraper.py
        # Then there should be nothing sent to message_queues

        # Mocking get_bets_data to return no bets
        mock_get_bets_data.return_value = {"data": "[]", "mtime": 1696014862.391}

        # Mock the configuration load
        mock_safe_load.return_value = {
            "username": "testuser",
            "password": "testpassword",
            "login_url": "https://testloginurl.com",
            "sing_api_url": "https://test_sing_url.com",
            "bet365_api_url": "https://test_bet365_url.com"
        }

        # Create a fake response object for the requests.Session.post/get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Some text that doesn't contain 'Username'"
        mock_response.json.return_value = {}

        mock_post.return_value = mock_response
        mock_get.return_value = mock_response

        # Run the scraper's start function
        self.scraper.start()

        # After running, check that message_queues is empty
        asyncio.run(self.scraper.periodic_task(mock_safe_load.return_value))
        self.assertFalse(self.scraper.bets_dict)

    def test_get_new_bets(self):
        # given there are some bets in the bets_dict from previous runs
        # when calling get_new_bets with new bets
        # then it should return only the new bets

        # Setting up the initial state: Given there are some bets in the bets_dict from previous runs
        url = "https://sample.url"

        bet = {'pin_fix': 'bet1', 'hours_to_start': 1, 'league': 'LeagueA', 'home_team': 'TeamA',
               'away_team': 'TeamB', 'bet_type': '1', 'mod': 0, 'price': 2.0, 'bet_class': 'classA'}
        bet_hash = str(hash(frozenset(bet.items())))

        self.scraper.bets_dict[url] = {
            bet_hash: bet,
        }

        # The new data: When calling get_new_bets with new bets
        data = json.dumps([
            {'pin_fix': 'bet1', 'hours_to_start': 1, 'league': 'LeagueA', 'home_team': 'TeamA',
             'away_team': 'TeamB', 'bet_type': '1', 'mod': 0, 'price': 2.0, 'bet_class': 'classA'},
            {'pin_fix': 'bet2', 'hours_to_start': 2, 'league': 'LeagueB', 'home_team': 'TeamC',
             'away_team': 'TeamD', 'bet_type': '2', 'mod': 1, 'price': 1.5, 'bet_class': 'classB'},
        ])

        new_bets = self.scraper.get_new_bets(url, data)

        # Then it should return only the new bets
        self.assertEqual(len(new_bets), 1)
        self.assertEqual(new_bets[0]['pin_fix'], 'bet2')

    @patch.object(BetSite, "get_bets_data")
    def test_get_and_parse_data_new_sing_data(self, mock_get_bets_data):
        # Mock the get_bets_data response for sing and bet365
        # Given we have old bets data in the bets_dict of sublist (0,1) of mock data
        # and mocking the get_bets_data response for sing and bet365 with sing having 12 bets and bet365 having 0 bets
        # When calling get_and_parse_data
        # Then it should return only the new sing data

        with open('../test_data.json', 'rb') as f:
            sing_mock_data = json.loads(f.read())

            bet365_mock_data = {
                'mtime': 'some_old_time',
                'data': "[]"
            }

            mock_get_bets_data.side_effect = [sing_mock_data, bet365_mock_data]

            config = {
                "sing_api_url": "https://test_sing_url.com",
                "bet365_api_url": "https://test_bet365_url.com",
            }

            sublist_of_mock_data = json.loads(sing_mock_data['data'])[0:1]
            self.scraper.bets_dict[config["sing_api_url"]] = sublist_of_mock_data

            result = asyncio.run(self.scraper.get_and_parse_data(config))

            # Check if only sing data is in the message queue
            self.assertEqual(len(result["sing"]), 11)
            self.assertEqual(len(result["bet365"]), 0)

    async def test_single_iteration_of_periodic_task(self):
        scraper = Scraper()
        config = {}  # Mock config as necessary

        # Create async magic mocks for the async functions
        scraper.get_and_parse_data = MagicMock(side_effect=asyncio.coroutine(MagicMock())())
        scraper.send_data_to_bot = MagicMock(side_effect=asyncio.coroutine(MagicMock())())

        # Run the periodic_task for a short time and then cancel it
        task = asyncio.create_task(scraper.periodic_task(config))
        await asyncio.sleep(0.1)  # Sleep long enough for the loop to have executed once
        task.cancel()

        # Check if the methods have been called
        scraper.get_and_parse_data.assert_called_once()
        scraper.send_data_to_bot.assert_called_once()


if __name__ == '__main__':
    unittest.main()
