import asyncio
import unittest
from unittest.mock import patch, MagicMock

from integrations.scraper import Scraper


class TestSendDataToBot(unittest.TestCase):
    def setUp(self):
        self.scraper = Scraper()
        self.config = {
            "bot_token": "test_token",
            "chat_sing_id": "1234",
            "chat_bet365_id": "5678"
        }

    @patch("requests.post")
    def test_empty_message_queue(self, mock_post):
        message_queues = {}
        asyncio.run(self.scraper.send_data_to_bot(message_queues, self.config))
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_only_sing_in_message_queue(self, mock_post):
        message_queues = {"sing": ["Test message for sing"]}
        asyncio.run(self.scraper.send_data_to_bot(message_queues, self.config))
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_only_bet365_in_message_queue(self, mock_post):
        message_queues = {"bet365": ["Test message for bet365"]}
        asyncio.run(self.scraper.send_data_to_bot(message_queues, self.config))
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_both_in_message_queue(self, mock_post):
        message_queues = {
            "sing": ["Test message for sing"],
            "bet365": ["Test message for bet365"]
        }
        asyncio.run(self.scraper.send_data_to_bot(message_queues, self.config))
        # Ensure that the post request was made twice, once for sing and once for bet365
        self.assertEqual(mock_post.call_count, 2)


if __name__ == '__main__':
    unittest.main()
