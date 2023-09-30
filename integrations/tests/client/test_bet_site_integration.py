import unittest
from unittest.mock import patch, Mock

from integrations.client.bet_site import BetSite


class TestBetSiteIntegration(unittest.TestCase):

    def setUp(self):
        self.bet_site = BetSite()
        self.login_url = "https://example.com/login"
        self.data_url = "https://example.com/data"

    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_successful_login_and_data_retrieval(self, mock_get, mock_post):
        # Mock the successful login response
        mock_post.return_value = Mock(status_code=200, text="Login Successful")

        # Mock the successful get data response
        mock_get.return_value = Mock(status_code=200, json=lambda: {"key": "value"}, text="something")

        self.assertTrue(self.bet_site.login("testuser", "testpassword", self.login_url))
        data = self.bet_site.get_bets_data(self.data_url)
        self.assertEqual(data, {"key": "value"})

    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_relogin_on_session_expiry(self, mock_get, mock_post):
        # Mock the successful login response
        mock_post.return_value = Mock(status_code=200, text="Login Successful")

        # First mock the expired session response, then mock a successful data retrieval
        mock_get.side_effect = [Mock(status_code=200, text="Username"),  # Session expired
                                Mock(status_code=200, json=lambda: {"key": "value"}, text="something")]  # Successful data retrieval

        self.assertTrue(self.bet_site.login("testuser", "testpassword", self.login_url))
        data = self.bet_site.get_bets_data(self.data_url)
        self.assertEqual(data, {"key": "value"})


if __name__ == "__main__":
    unittest.main()
