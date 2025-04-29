#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example for working with custom post types using the WordPress REST API Python Client.
"""

import sys
import os
import logging

# Add parent directory to path to import wp_api in development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth
from wp_api.exceptions import WPAPIError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('wp_api_example')

def main():
    """Run example demonstrating custom post type functionality."""
    
    # Replace these values with your WordPress site details
    wp_url = "https://example.com"
    username = "your_username"
    app_password = "your_app_password"
    
    logger.info(f"Connecting to WordPress site: {wp_url}")
    
    try:
        # Initialize authentication and client
        auth = ApplicationPasswordAuth(username=username, app_password=app_password)
        client = WPClient(base_url=wp_url, auth=auth)
        
        # Replace 'product' with your actual custom post type
        custom_post_type = 'product'
        logger.info(f"Working with custom post type: {custom_post_type}")
        
        # Get custom post type handler
        products = client.get_custom_post_type(custom_post_type)
        
        # List items
        logger.info(f"Fetching {custom_post_type} items...")
        items = products.list(per_page=5, status="publish")
        
        for item in items:
            logger.info(f"ID: {item['id']}, Title: {item['title']['rendered']}")
        
        # Get custom fields for a specific item
        if items:
            product_id = items[0]['id']
            logger.info(f"Fetching meta fields for {custom_post_type} ID: {product_id}")
            
            product_meta = products.get_meta()
            meta_fields = product_meta.get_all(product_id)
            
            logger.info(f"Meta fields: {meta_fields}")
            
            # Create or update a meta field (uncomment to run)
            # logger.info(f"Updating meta field for {custom_post_type} ID: {product_id}")
            # updated_meta = product_meta.update_or_create(product_id, "test_field", "test_value")
            # logger.info(f"Updated meta: {updated_meta}")
        
        # Create a new item (uncomment to run)
        # logger.info(f"Creating new {custom_post_type}...")
        # new_product = products.create(
        #     title=f"Test {custom_post_type.capitalize()}",
        #     content=f"This is a test {custom_post_type}.",
        #     status="draft",
        #     # Add custom fields as needed
        #     # custom_field: "value"
        # )
        # logger.info(f"Created {custom_post_type} with ID: {new_product['id']}")
        
    except WPAPIError as e:
        logger.error(f"WordPress API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()