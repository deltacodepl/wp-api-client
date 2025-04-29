#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic usage example for the WordPress REST API Python Client.
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to path to import wp_api in development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth
from wp_api.exceptions import (
    WPAPIError,
    WPAPIAuthError,
    WPAPINotFoundError,
    WPAPIPermissionError
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wp_api_example')

def main():
    """Run a basic example demonstrating wp_api functionality."""
    
    # Replace these values with your WordPress site details
    wp_url = "https://example.com"
    username = "your_username"
    app_password = "your_app_password"
    
    logger.info(f"Connecting to WordPress site: {wp_url}")
    
    try:
        # Initialize authentication and client
        auth = ApplicationPasswordAuth(username=username, app_password=app_password)
        client = WPClient(base_url=wp_url, auth=auth)
        
        # Get site information
        logger.info("Fetching site information...")
        endpoints = client.discover_endpoints()
        
        if 'name' in endpoints and 'description' in endpoints:
            logger.info(f"Site name: {endpoints['name']}")
            logger.info(f"Site description: {endpoints['description']}")
        
        # Get recent posts
        logger.info("Fetching recent posts...")
        posts = client.posts.list(per_page=5, status="publish")
        
        for post in posts:
            logger.info(f"Post ID: {post['id']}, Title: {post['title']['rendered']}")
        
        # Create a new post (uncomment to run)
        # logger.info("Creating a new post...")
        # new_post = client.posts.create(
        #     title=f"Test Post - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        #     content="This is a test post created via the WordPress REST API Python Client.",
        #     status="draft"
        # )
        # logger.info(f"Created post with ID: {new_post['id']}")
        
    except WPAPIAuthError as e:
        logger.error(f"Authentication error: {e}")
    except WPAPIPermissionError as e:
        logger.error(f"Permission denied: {e}")
    except WPAPINotFoundError as e:
        logger.error(f"Resource not found: {e}")
    except WPAPIError as e:
        logger.error(f"WordPress API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()