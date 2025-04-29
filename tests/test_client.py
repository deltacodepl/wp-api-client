"""Tests for `wp_api` client module."""

import unittest
from unittest import mock

import requests

from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth
from wp_api.exceptions import WPAPIError, WPAPIAuthError, WPAPINotFoundError


class TestWPClient(unittest.TestCase):
    """Tests for `wp_api` client class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://example.com"
        self.auth = mock.Mock(spec=ApplicationPasswordAuth)
        self.client = WPClient(base_url=self.base_url, auth=self.auth)
    
    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.base_url, "https://example.com/wp-json/wp/v2/")
        self.assertEqual(self.client.root_url, "https://example.com/wp-json/")
        self.assertEqual(self.client.auth, self.auth)
        self.auth.authenticate.assert_called_once()
    
    @mock.patch('requests.Session.get')
    def test_get(self, mock_get):
        """Test GET request."""
        # Setup mock response
        mock_response = mock.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": 1, "title": "Test Post"}
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.client.get("posts/1")
        
        # Assertions
        mock_get.assert_called_once_with(
            "https://example.com/wp-json/wp/v2/posts/1",
            params=None,
            timeout=30
        )
        self.assertEqual(result, {"id": 1, "title": "Test Post"})
    
    @mock.patch('requests.Session.get')
    def test_get_error(self, mock_get):
        """Test GET request with error."""
        # Setup mock response for error
        mock_response = mock.Mock()
        http_error = requests.exceptions.HTTPError("404 Client Error")
        mock_response.raise_for_status.side_effect = http_error
        mock_response.status_code = 404
        mock_response.json.return_value = {"code": "rest_post_invalid_id", "message": "Invalid post ID."}
        
        # Mock the exception response
        http_error.response = mock_response
        mock_get.return_value = mock_response
        
        # Call the method and check exception
        with self.assertRaises(WPAPIError):
            self.client.get("posts/999")
    
    @mock.patch('requests.Session.post')
    def test_post(self, mock_post):
        """Test POST request."""
        # Setup mock response
        mock_response = mock.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": 1, "title": "New Post"}
        mock_post.return_value = mock_response
        
        # Call the method
        data = {"title": "New Post", "content": "Post content", "status": "publish"}
        result = self.client.post("posts", data)
        
        # Assertions
        self.assertEqual(result, {"id": 1, "title": "New Post"})
        mock_post.assert_called_once()
    
    def test_posts_property(self):
        """Test posts property."""
        posts = self.client.posts
        self.assertEqual(posts.endpoint, "posts")
    
    def test_pages_property(self):
        """Test pages property."""
        pages = self.client.pages
        self.assertEqual(pages.endpoint, "pages")


if __name__ == '__main__':
    unittest.main()