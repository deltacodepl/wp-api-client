#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example demonstrating advanced error handling with the WordPress REST API Python Client.
"""

import sys
import os
import logging
import json

# Add parent directory to path to import wp_api in development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth, BasicAuth
from wp_api.exceptions import (
    WPAPIError,
    WPAPIAuthError,
    WPAPIRequestError,
    WPAPIRateLimitError,
    WPAPINotFoundError,
    WPAPIPermissionError,
    WPAPIValidationError,
    WPAPIBadRequestError,
    WPAPIServerError,
    WPAPITimeoutError,
    WPAPIConnectionError
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wp_api_example')

def handle_api_error(error):
    """Handle different types of API errors with appropriate responses."""
    
    if isinstance(error, WPAPIAuthError):
        logger.error(f"Authentication error: {error}")
        logger.error("Please check your credentials and try again.")
        
    elif isinstance(error, WPAPIPermissionError):
        logger.error(f"Permission denied: {error}")
        logger.error("Your user account doesn't have sufficient permissions.")
        
    elif isinstance(error, WPAPINotFoundError):
        logger.error(f"Resource not found: {error}")
        
    elif isinstance(error, WPAPIRateLimitError):
        logger.error(f"Rate limit exceeded: {error}")
        logger.error("Please reduce your request frequency and try again later.")
        
    elif isinstance(error, WPAPIValidationError) or isinstance(error, WPAPIBadRequestError):
        logger.error(f"Invalid request: {error}")
        if hasattr(error, 'error_data') and error.error_data:
            logger.error(f"Error details: {json.dumps(error.error_data, indent=2)}")
            
    elif isinstance(error, WPAPIServerError):
        logger.error(f"WordPress server error: {error}")
        logger.error("The WordPress site is experiencing internal issues.")
        
    elif isinstance(error, WPAPITimeoutError):
        logger.error(f"Request timeout: {error}")
        logger.error("The WordPress site took too long to respond.")
        
    elif isinstance(error, WPAPIConnectionError):
        logger.error(f"Connection error: {error}")
        logger.error("Could not connect to the WordPress site.")
        
    elif isinstance(error, WPAPIRequestError):
        logger.error(f"Request error: {error}")
        if hasattr(error, 'status_code') and error.status_code:
            logger.error(f"Status code: {error.status_code}")
            
    else:
        logger.error(f"Unknown WordPress API error: {error}")


def deliberately_cause_errors(client):
    """Demonstrate different error scenarios."""
    
    # 1. Try to access a non-existent post (404)
    try:
        logger.info("Attempting to fetch a non-existent post (should fail with 404)...")
        client.posts.get(999999999)
    except WPAPIError as e:
        handle_api_error(e)
    
    # 2. Try to create a post with invalid data (400)
    try:
        logger.info("Attempting to create a post with invalid data (should fail with validation error)...")
        # Missing required 'title' field
        client.posts.create(content="Test content", invalid_field="test")
    except WPAPIError as e:
        handle_api_error(e)
    
    # 3. Try to access an endpoint with insufficient permissions
    try:
        logger.info("Attempting to access an endpoint with insufficient permissions...")
        # Typically settings endpoint requires admin privileges
        client.settings.update(title="New Title")
    except WPAPIError as e:
        handle_api_error(e)
    
    # 4. Try with incorrect authentication
    try:
        logger.info("Attempting with incorrect authentication...")
        bad_auth = BasicAuth(username="wrong_user", password="wrong_pass")
        bad_client = WPClient(base_url=client.base_url.replace("/wp-json/wp/v2/", ""), auth=bad_auth)
        bad_client.posts.list()
    except WPAPIError as e:
        handle_api_error(e)


def main():
    """Run error handling examples."""
    
    # Replace these values with your WordPress site details
    wp_url = "https://example.com"
    username = "your_username"
    app_password = "your_app_password"
    
    logger.info(f"Connecting to WordPress site: {wp_url}")
    
    try:
        # Initialize authentication and client with retry settings
        auth = ApplicationPasswordAuth(username=username, app_password=app_password)
        client = WPClient(
            base_url=wp_url, 
            auth=auth,
            timeout=30,
            retry_count=2,
            retry_backoff_factor=0.5
        )
        
        # Run error examples
        deliberately_cause_errors(client)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()