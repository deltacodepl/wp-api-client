"""Tests for `wp_api` authentication module."""

import unittest
from unittest import mock
import base64

import requests

from wp_api.auth import BasicAuth, ApplicationPasswordAuth, OAuth1


class TestBasicAuth(unittest.TestCase):
    """Tests for BasicAuth class."""
    
    def test_authenticate(self):
        """Test BasicAuth authentication."""
        auth = BasicAuth(username="testuser", password="testpass")
        session = mock.Mock(spec=requests.Session)
        session.headers = {}
        
        auth.authenticate(session)
        
        # Check that the Authorization header was set correctly
        auth_string = "testuser:testpass"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        expected_header = f"Basic {encoded_auth}"
        
        self.assertEqual(session.headers.get("Authorization"), expected_header)


class TestApplicationPasswordAuth(unittest.TestCase):
    """Tests for ApplicationPasswordAuth class."""
    
    def test_authenticate(self):
        """Test ApplicationPasswordAuth authentication."""
        auth = ApplicationPasswordAuth(username="testuser", app_password="app_testpass")
        session = mock.Mock(spec=requests.Session)
        session.headers = {}
        
        auth.authenticate(session)
        
        # Check that the Authorization header was set correctly
        auth_string = "testuser:app_testpass"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        expected_header = f"Basic {encoded_auth}"
        
        self.assertEqual(session.headers.get("Authorization"), expected_header)


class TestOAuth1(unittest.TestCase):
    """Tests for OAuth1 class."""
    
    def test_init(self):
        """Test OAuth1 initialization."""
        auth = OAuth1(
            consumer_key="consumer_key",
            consumer_secret="consumer_secret",
            token="token",
            token_secret="token_secret"
        )
        
        self.assertEqual(auth.consumer_key, "consumer_key")
        self.assertEqual(auth.consumer_secret, "consumer_secret")
        self.assertEqual(auth.token, "token")
        self.assertEqual(auth.token_secret, "token_secret")
    
    @mock.patch('uuid.uuid4')
    @mock.patch('time.time')
    def test_authenticate(self, mock_time, mock_uuid):
        """Test OAuth1 authentication modifies the request method."""
        # Mock time and UUID for predictable values
        mock_time.return_value = 1500000000
        mock_uuid.return_value.hex = "test_uuid"
        
        auth = OAuth1(
            consumer_key="consumer_key",
            consumer_secret="consumer_secret"
        )
        
        session = mock.Mock(spec=requests.Session)
        original_request = session.request
        
        # Call authenticate
        auth.authenticate(session)
        
        # Verify request method was patched
        self.assertNotEqual(session.request, original_request)
        
        # Test the patched method by calling it
        url = "https://example.com/wp-json/wp/v2/posts"
        session.request("GET", url)
        
        # Assert original_request was called
        original_request.assert_called_once()


if __name__ == '__main__':
    unittest.main()