#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WordPress Backup Tool

This script downloads content from a WordPress site using the WordPress REST API
and saves it locally with an option to upload to Amazon S3. Authentication is optional -
the script can backup publicly available content without credentials.

Usage:
    python wp_backup.py --url https://example.com [options]

Features:
- Works with or without authentication
- Downloads posts, pages, media files, taxonomies, and other public content
- Saves metadata in JSON format
- Downloads all media files
- Organizes content in a structured folder hierarchy
- Optional S3 backup
- Detailed logging and progress reporting
- Comprehensive error handling
"""

import os
import sys
import json
import time
import logging
import shutil
import argparse
import concurrent.futures
from datetime import datetime
import requests
import platform
import traceback
import signal
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from pathlib import Path
from urllib.parse import urlparse

# Try importing boto3 for S3 support (optional dependency)
try:
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

# Import the WordPress REST API client
try:
    from wp_api import WPClient
    from wp_api.auth import BasicAuth, ApplicationPasswordAuth
    from wp_api.exceptions import (
        WPAPIError, 
        WPAPIAuthError, 
        WPAPINotFoundError, 
        WPAPIPermissionError,
        WPAPIRequestError,
        WPAPIRateLimitError
    )
except ImportError:
    print("Error: WordPress REST API client library not found. Install with: pip install wp-api-client")
    sys.exit(1)

# Version
__version__ = '1.1.0'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('wp_backup')

# Handle keyboard interrupts gracefully
def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully."""
    logger.info("Backup interrupted by user. Exiting...")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

class WordPressBackup:
    """WordPress site backup tool using the WordPress REST API."""
    
    # Default content types to backup (only publicly accessible by default)
    PUBLIC_CONTENT_TYPES = [
        'posts', 'pages', 'media', 'categories', 
        'tags', 'comments', 'custom_post_types'
    ]
    
    # Content types that typically require authentication
    AUTH_CONTENT_TYPES = [
        'users', 'settings'
    ]
    
    # All supported content types
    ALL_CONTENT_TYPES = PUBLIC_CONTENT_TYPES + AUTH_CONTENT_TYPES
    
    # Custom post types to check for
    COMMON_CUSTOM_POST_TYPES = [
        'product', 'portfolio', 'testimonial', 'team', 'faq',
        'service', 'project', 'event', 'course', 'review'
    ]
    
    def __init__(
        self, 
        site_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        output_dir: str = "./wp_backup",
        s3_bucket: Optional[str] = None,
        s3_prefix: Optional[str] = None,
        content_types: Optional[List[str]] = None,
        max_items_per_type: int = 1000,
        media_max_workers: int = 5,
        skip_media: bool = False,
        auth_type: str = 'app_password',
        debug: bool = False,
        ignore_ssl_errors: bool = False,
        force_public: bool = False
    ):
        """
        Initialize the WordPress backup tool.
        
        Args:
            site_url: URL of the WordPress site
            username: WordPress username (optional)
            password: WordPress password or application password (optional)
            output_dir: Local directory to save backups
            s3_bucket: Optional S3 bucket name for backup
            s3_prefix: Optional S3 key prefix (folder path)
            content_types: List of content types to backup (default: all public)
            max_items_per_type: Maximum items to retrieve per content type
            media_max_workers: Maximum parallel workers for downloading media
            skip_media: Whether to skip downloading media files
            auth_type: Authentication type ('basic' or 'app_password')
            debug: Enable debug logging
            ignore_ssl_errors: Ignore SSL certificate errors
            force_public: Force public-only mode even if credentials are provided
        """
        self.site_url = site_url.rstrip('/')
        self.username = username or os.environ.get('WP_USER')
        self.password = password or os.environ.get('WP_PASSWORD')
        self.output_dir = Path(output_dir)
        self.s3_bucket = s3_bucket or os.environ.get('S3_BUCKET')
        self.s3_prefix = s3_prefix or os.environ.get('S3_PREFIX', '')
        self.max_items_per_type = max_items_per_type
        self.media_max_workers = media_max_workers
        self.skip_media = skip_media
        self.auth_type = auth_type
        self.ignore_ssl_errors = ignore_ssl_errors
        self.force_public = force_public
        self.client = None
        self.s3_client = None
        
        # Configure logging
        if debug:
            logger.setLevel(logging.DEBUG)
        
        # Determine authentication status first
        self.is_authenticated = False
        self.auth_mode = "public"
        
        if self.username and self.password and not force_public:
            self.is_authenticated = True
            self.auth_mode = auth_type
            logger.info("Authentication credentials provided. Running in authenticated mode.")
        else:
            logger.info("No authentication credentials provided or force_public enabled. Running in public access mode.")
        
        # Set appropriate content types based on authentication status
        if content_types:
            self.content_types = content_types
            if not self.is_authenticated:
                # Filter out auth-only content types if not authenticated
                auth_only = set(self.AUTH_CONTENT_TYPES)
                filtered_types = [ct for ct in self.content_types if ct not in auth_only]
                if len(filtered_types) < len(self.content_types):
                    removed = set(self.content_types) - set(filtered_types)
                    logger.warning(f"Removing content types that require authentication: {', '.join(removed)}")
                    self.content_types = filtered_types
        else:
            # Default to all supported types if authenticated, otherwise only public
            self.content_types = self.ALL_CONTENT_TYPES if self.is_authenticated else self.PUBLIC_CONTENT_TYPES
            
        # Initialize backup info dictionary
        self.backup_info = {
            'site_url': site_url,
            'backup_date': datetime.now().isoformat(),
            'content_types': self.content_types,
            'auth_mode': self.auth_mode,
            'version': __version__,
            'system_info': {
                'python_version': platform.python_version(),
                'platform': platform.platform(),
                'machine': platform.machine()
            },
            'stats': {},
        }
        
        # Create output directory
        if not self.output_dir.exists():
            try:
                self.output_dir.mkdir(parents=True)
            except OSError as e:
                logger.error(f"Failed to create output directory: {e}")
                raise ValueError(f"Cannot create output directory: {str(e)}")
        
        # Initialize S3 client if needed
        if self.s3_bucket:
            if not S3_AVAILABLE:
                raise ImportError("S3 backup requested but boto3 is not installed. "
                                "Install with: pip install boto3")
            try:
                self.s3_client = boto3.client('s3')
                logger.info(f"S3 backup will be saved to s3://{self.s3_bucket}/{self.s3_prefix}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                raise
        
        # Initialize WordPress client last
        try:
            self._init_wp_client()
        except Exception as e:
            logger.error(f"Failed to initialize WordPress client: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def _init_wp_client(self) -> None:
        """Initialize the WordPress API client with or without authentication."""
        try:
            logger.info(f"Connecting to WordPress site: {self.site_url}")
            
            # Initialize client with or without authentication
            if self.is_authenticated:
                # Select authentication method if credentials are provided
                if self.auth_type.lower() == 'basic':
                    auth = BasicAuth(username=self.username, password=self.password)
                else:  # default to app_password
                    auth = ApplicationPasswordAuth(username=self.username, app_password=self.password)
                
                # Initialize client with authentication and retry settings
                self.client = WPClient(
                    base_url=self.site_url,
                    auth=auth,
                    timeout=30,
                    retry_count=3,
                    retry_backoff_factor=0.5,
                    verify_ssl=not self.ignore_ssl_errors
                )
            else:
                # Initialize client without authentication for public access only
                self.client = WPClient(
                    base_url=self.site_url,
                    auth=None,  # No authentication
                    timeout=30,
                    retry_count=3,
                    retry_backoff_factor=0.5,
                    verify_ssl=not self.ignore_ssl_errors
                )
            
            # Test connection by getting site info
            try:
                endpoints = self.client.discover_endpoints()
                site_name = endpoints.get('name', self.site_url)
                site_desc = endpoints.get('description', 'No description available')
                logger.info(f"Successfully connected to: {site_name} - {site_desc}")
                self.backup_info['site_name'] = site_name
                self.backup_info['site_description'] = site_desc
            except WPAPIError as e:
                logger.error(f"Failed to connect to WordPress site: {e}")
                raise
                
        except WPAPIAuthError as e:
            if self.is_authenticated:
                logger.error(f"Authentication error: {e}")
                raise
            else:
                # If not authenticated and auth error occurs, we should still try to continue
                # with public data only
                logger.warning("Authentication failed, but continuing in public-only mode")
                
                # Reinitialize client without auth to ensure we're in public mode
                self.client = WPClient(
                    base_url=self.site_url,
                    auth=None,
                    timeout=30,
                    retry_count=3,
                    retry_backoff_factor=0.5,
                    verify_ssl=not self.ignore_ssl_errors
                )
        except Exception as e:
            logger.error(f"Failed to initialize WordPress client: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def run_backup(self) -> Dict[str, Any]:
        """
        Run the complete backup process.
        
        Returns:
            Dictionary containing backup information and statistics
        """
        start_time = time.time()
        logger.info(f"Starting WordPress backup for {self.site_url}")
        
        try:
            # Save initial info with pending status
            self.backup_info['status'] = 'in_progress'
            self._save_backup_info()
            
            # Detect custom post types
            if 'custom_post_types' in self.content_types:
                self._detect_custom_post_types()
            
            # Back up each content type
            for content_type in self.content_types:
                if content_type == 'custom_post_types':
                    continue  # Already processed during detection
                
                try:
                    if hasattr(self, f"_backup_{content_type}"):
                        logger.info(f"Backing up {content_type}...")
                        backup_method = getattr(self, f"_backup_{content_type}")
                        backup_method()
                    else:
                        logger.warning(f"No backup method for content type: {content_type}")
                except WPAPIPermissionError as e:
                    logger.warning(f"Permission denied for {content_type}. This endpoint may require authentication: {e}")
                    self.backup_info['stats'][content_type] = {'error': f"Permission denied: {str(e)}"}
                except WPAPINotFoundError as e:
                    logger.warning(f"Endpoint not found for {content_type}: {e}")
                    self.backup_info['stats'][content_type] = {'error': f"Not found: {str(e)}"}
                except WPAPIError as e:
                    logger.error(f"Error backing up {content_type}: {e}")
                    self.backup_info['stats'][content_type] = {'error': str(e)}
                except Exception as e:
                    logger.error(f"Unexpected error backing up {content_type}: {e}")
                    logger.debug(traceback.format_exc())
                    self.backup_info['stats'][content_type] = {'error': str(e)}
            
            # Upload to S3 if configured
            if self.s3_bucket:
                try:
                    self._upload_to_s3()
                except Exception as e:
                    logger.error(f"Error uploading to S3: {e}")
                    logger.debug(traceback.format_exc())
                    self.backup_info['s3_upload_error'] = str(e)
                
            # Calculate total time
            elapsed_time = time.time() - start_time
            self.backup_info['elapsed_seconds'] = elapsed_time
            self.backup_info['status'] = 'completed'
            
            # Save final backup info
            self._save_backup_info()
            
            logger.info(f"Backup completed in {elapsed_time:.2f} seconds")
            
            return self.backup_info
            
        except KeyboardInterrupt:
            logger.info("Backup process interrupted by user")
            self.backup_info['status'] = 'interrupted'
            self._save_backup_info()  # Save info even on interruption
            raise
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            logger.debug(traceback.format_exc())
            self.backup_info['status'] = 'failed'
            self.backup_info['error'] = str(e)
            self._save_backup_info()  # Save info even on failure
            raise
    
    def _detect_custom_post_types(self) -> None:
        """Detect and backup custom post types."""
        logger.info("Detecting custom post types...")
        
        try:
            # First try to get registered post types through the WordPress API
            endpoints = self.client.discover_endpoints()
            custom_post_types = []
            
            if 'routes' in endpoints:
                for route, data in endpoints['routes'].items():
                    # Check for post type endpoints
                    if route.startswith('/wp/v2/') and not any(route.endswith(f"/{cpt}") 
                                                              for cpt in ['posts', 'pages', 'media']):
                        # Extract post type from route
                        post_type = route.split('/')[-1]
                        if post_type and post_type not in ['', 'posts', 'pages', 'media']:
                            custom_post_types.append(post_type)
            
            # If no post types found through API discovery, try common ones
            if not custom_post_types:
                logger.info("No custom post types found via API discovery, trying common types...")
                for cpt in self.COMMON_CUSTOM_POST_TYPES:
                    try:
                        # Test if this post type exists
                        cpt_client = self.client.get_custom_post_type(cpt)
                        items = cpt_client.list(per_page=1)
                        if items:
                            custom_post_types.append(cpt)
                            logger.info(f"Found active custom post type: {cpt}")
                    except WPAPINotFoundError:
                        # This post type doesn't exist, skip it
                        pass
                    except WPAPIPermissionError:
                        # This post type exists but requires authentication
                        logger.debug(f"Custom post type {cpt} exists but requires authentication")
                        # Skip in public mode, otherwise report the error
                        if not self.is_authenticated:
                            logger.info(f"Skipping {cpt} as it requires authentication")
                    except WPAPIError as e:
                        logger.debug(f"Error checking post type {cpt}: {e}")
            
            # Backup each custom post type found
            if 'custom_post_types' not in self.backup_info:
                self.backup_info['custom_post_types'] = []
                
            self.backup_info['custom_post_types'] = custom_post_types
            
            for cpt in custom_post_types:
                logger.info(f"Backing up custom post type: {cpt}")
                self._backup_custom_post_type(cpt)
                
            logger.info(f"Found and processed {len(custom_post_types)} custom post types")
            
        except WPAPIPermissionError as e:
            logger.warning(f"Permission denied when detecting custom post types: {e}")
            logger.warning("This might be due to restricted access to the WordPress REST API discovery endpoint")
        except WPAPIError as e:
            logger.error(f"Failed to detect custom post types: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error detecting custom post types: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def _backup_posts(self) -> None:
        """Backup all posts."""
        self._backup_content_type('posts', self.client.posts)
    
    def _backup_pages(self) -> None:
        """Backup all pages."""
        self._backup_content_type('pages', self.client.pages)
    
    def _backup_media(self) -> None:
        """Backup all media items and download files."""
        media_items = self._backup_content_type('media', self.client.media)
        
        if not self.skip_media and media_items:
            self._download_media_files(media_items)
    
    def _backup_categories(self) -> None:
        """Backup all categories."""
        self._backup_content_type('categories', self.client.categories)
    
    def _backup_tags(self) -> None:
        """Backup all tags."""
        self._backup_content_type('tags', self.client.tags)
    
    def _backup_users(self) -> None:
        """Backup all users."""
        # This typically requires authentication
        if not self.is_authenticated:
            logger.warning("Users endpoint typically requires authentication, attempting anyway...")
        self._backup_content_type('users', self.client.users)
    
    def _backup_comments(self) -> None:
        """Backup all comments."""
        self._backup_content_type('comments', self.client.comments)
    
    def _backup_settings(self) -> None:
        """Backup WordPress settings."""
        # Settings almost always require authentication
        if not self.is_authenticated:
            logger.warning("Settings endpoint requires authentication, attempting anyway...")
        
        try:
            settings = self.client.settings.get()
            if settings:
                settings_dir = self.output_dir / 'settings'
                settings_dir.mkdir(exist_ok=True)
                settings_file = settings_dir / "settings.json"
                self._save_json_file(settings_file, settings)
                
                self.backup_info['stats']['settings'] = {
                    'count': 1
                }
                logger.info(f"Successfully backed up WordPress settings")
        except WPAPIPermissionError:
            logger.warning("Permission denied when accessing settings - this endpoint requires authentication")
            self.backup_info['stats']['settings'] = {
                'error': 'Permission denied - requires authentication'
            }
        except WPAPIError as e:
            logger.error(f"Error backing up settings: {e}")
            self.backup_info['stats']['settings'] = {
                'error': str(e)
            }
    
    def _backup_custom_post_type(self, post_type: str) -> None:
        """
        Backup a specific custom post type.
        
        Args:
            post_type: Custom post type slug
        """
        cpt_client = self.client.get_custom_post_type(post_type)
        items = self._backup_content_type(f'cpt_{post_type}', cpt_client)
        
        # Try to backup custom fields (meta) for this post type
        if items and self.is_authenticated:  # Meta typically requires authentication
            try:
                meta_client = cpt_client.get_meta()
                meta_dir = self.output_dir / f'cpt_{post_type}_meta'
                meta_dir.mkdir(exist_ok=True)
                
                meta_successes = 0
                meta_errors = 0
                
                for item in items:
                    try:
                        item_id = item['id']
                        meta_data = meta_client.get_all(item_id)
                        if meta_data:
                            meta_file = meta_dir / f"{item_id}.json"
                            with open(meta_file, 'w', encoding='utf-8') as f:
                                json.dump(meta_data, f, indent=2)
                            meta_successes += 1
                    except WPAPIError as e:
                        logger.warning(f"Failed to get meta for {post_type} ID {item['id']}: {e}")
                        meta_errors += 1
                    except Exception as e:
                        logger.warning(f"Unexpected error getting meta for {post_type} ID {item['id']}: {e}")
                        meta_errors += 1
                
                # Update stats
                self.backup_info['stats'][f'cpt_{post_type}_meta'] = {
                    'count': meta_successes,
                    'errors': meta_errors
                }
                
            except Exception as e:
                logger.warning(f"Failed to backup meta for {post_type}: {e}")
                logger.debug(traceback.format_exc())
    
    def _backup_content_type(self, type_name: str, endpoint_client) -> List[Dict]:
        """
        Generic method to backup a content type.
        
        Args:
            type_name: Name of the content type (for file naming)
            endpoint_client: Endpoint client object from wp_api
        
        Returns:
            List of items retrieved
        """
        items = []
        page = 1
        total_items = 0
        per_page = 100  # Number of items per request
        
        # Create directory for this content type
        content_dir = self.output_dir / type_name
        try:
            content_dir.mkdir(exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directory for {type_name}: {e}")
            raise
        
        try:
            # Loop to get all items
            retry_count = 0
            max_retries = 5
            
            while total_items < self.max_items_per_type:
                try:
                    # Build parameters - use different ones depending on content type
                    params = {
                        'page': page,
                        'per_page': per_page
                    }
                    
                    # For posts, pages, and custom post types, adjust to handle public-only access 
                    if type_name in ['posts', 'pages'] or type_name.startswith('cpt_'):
                        if not self.is_authenticated:
                            # When not authenticated, we can only access published content
                            params['status'] = 'publish'
                    
                    batch = endpoint_client.list(**params)
                    
                    if not batch:
                        if page == 1:
                            logger.info(f"No {type_name} found")
                        break  # No more items
                    
                    items.extend(batch)
                    batch_count = len(batch)
                    total_items += batch_count
                    logger.info(f"Retrieved {batch_count} {type_name} (total: {total_items})")
                    
                    # Save this batch
                    batch_file = content_dir / f"page_{page}.json"
                    self._save_json_file(batch_file, batch)
                    
                    # Reset retry counter on success
                    retry_count = 0
                    
                    # Check if we got fewer items than requested, meaning we're at the end
                    if batch_count < per_page:
                        break
                        
                    page += 1
                    
                except WPAPIRateLimitError:
                    # Handle rate limiting with exponential backoff
                    retry_count += 1
                    if retry_count > max_retries:
                        logger.error(f"Maximum retries ({max_retries}) exceeded for {type_name} page {page}")
                        break
                        
                    wait_time = min(2 ** (retry_count - 1), 60)  # Cap at 60 seconds
                    logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    # Don't increment page, retry the same page
                
                except WPAPINotFoundError:
                    logger.warning(f"Endpoint not found for {type_name}")
                    break
                    
                except WPAPIPermissionError:
                    logger.warning(f"Permission denied for {type_name} - this endpoint may require authentication")
                    break
                    
                except WPAPIError as e:
                    logger.error(f"API error retrieving {type_name} (page {page}): {e}")
                    retry_count += 1
                    if retry_count > max_retries:
                        logger.error(f"Maximum retries ({max_retries}) exceeded for {type_name} page {page}")
                        break
                    
                    wait_time = min(2 ** (retry_count - 1), 30)
                    logger.warning(f"Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
            
            # Save all items to a single file as well
            if items:
                all_items_file = content_dir / "all.json"
                self._save_json_file(all_items_file, items)
            
            # Update backup stats
            self.backup_info['stats'][type_name] = {
                'count': len(items),
                'pages': page
            }
            
            return items
            
        except WPAPIPermissionError as e:
            logger.warning(f"Permission denied when accessing {type_name}: {e}")
            logger.warning("This endpoint may require authentication")
            self.backup_info['stats'][type_name] = {
                'error': f"Permission denied: {str(e)}"
            }
            return []
        except Exception as e:
            logger.error(f"Error backing up {type_name}: {e}")
            logger.debug(traceback.format_exc())
            self.backup_info['stats'][type_name] = {
                'error': str(e)
            }
            return []
    
    def _save_json_file(self, file_path: Path, data: Any) -> None:
        """
        Save data to a JSON file with error handling.
        
        Args:
            file_path: Path to save the file
            data: Data to save (must be JSON serializable)
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save JSON file {file_path}: {e}")
            logger.debug(traceback.format_exc())
            # Try to save with a simplified approach if the normal approach fails
            try:
                with open(f"{file_path}.simplified.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=True, default=str)
            except Exception:
                logger.error(f"Failed to save even simplified JSON for {file_path}")
    
    def _download_media_files(self, media_items: List[Dict]) -> None:
        """
        Download all media files.
        
        Args:
            media_items: List of media items from the API
        """
        logger.info(f"Downloading {len(media_items)} media files with {self.media_max_workers} workers...")
        
        # Create media files directory
        media_dir = self.output_dir / 'media_files'
        try:
            media_dir.mkdir(exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create media directory: {e}")
            raise
        
        # Track download statistics
        download_stats = {
            'total': len(media_items),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'bytes_downloaded': 0
        }
        
        # Create a progress tracker
        progress_interval = max(1, len(media_items) // 20)  # Update every ~5%
        last_progress_time = time.time()
        progress_update_interval = 5  # seconds
        
        # Function to show progress updates
        def show_progress():
            nonlocal last_progress_time
            current_time = time.time()
            if (download_stats['success'] + download_stats['failed'] + download_stats['skipped']) % progress_interval == 0 or \
               (current_time - last_progress_time) > progress_update_interval:
                completed = download_stats['success'] + download_stats['failed'] + download_stats['skipped']
                percent = (completed / download_stats['total']) * 100 if download_stats['total'] > 0 else 0
                mb_downloaded = download_stats['bytes_downloaded'] / (1024 * 1024)
                
                logger.info(f"Downloaded {completed}/{download_stats['total']} "
                           f"media files ({percent:.1f}%) - {mb_downloaded:.2f} MB")
                last_progress_time = current_time
                
                # Update backup info periodically for long-running downloads
                self.backup_info['stats']['media_files'] = download_stats.copy()
                self._save_backup_info()
        
        # Download media files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.media_max_workers) as executor:
            # Submit all downloads
            future_to_item = {
                executor.submit(self._download_media_file, item, media_dir): item
                for item in media_items
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    success, bytes_downloaded, error = future.result()
                    if success:
                        download_stats['success'] += 1
                        download_stats['bytes_downloaded'] += bytes_downloaded
                    elif error == 'skipped':
                        download_stats['skipped'] += 1
                    else:
                        download_stats['failed'] += 1
                        logger.warning(f"Failed to download media ID {item.get('id')}: {error}")
                        
                    # Show progress
                    show_progress()
                        
                except Exception as e:
                    download_stats['failed'] += 1
                    logger.error(f"Error downloading media ID {item.get('id', 'unknown')}: {e}")
                    logger.debug(traceback.format_exc())
                    show_progress()
        
        # Update backup info
        total_mb = download_stats['bytes_downloaded'] / (1024 * 1024)
        logger.info(f"Media download complete: {download_stats['success']} successful, "
                   f"{download_stats['failed']} failed, {download_stats['skipped']} skipped, "
                   f"{total_mb:.2f} MB downloaded")
        
        self.backup_info['stats']['media_files'] = download_stats
    
    def _download_media_file(self, media_item: Dict, media_dir: Path) -> Tuple[bool, int, str]:
        """
        Download a single media file.
        
        Args:
            media_item: Media item data from API
            media_dir: Directory to save media files
        
        Returns:
            Tuple of (success, bytes_downloaded, error_message)
        """
        source_url = media_item.get('source_url')
        if not source_url:
            return False, 0, "No source URL found"
        
        # Get filename from URL or media item data
        filename = None
        if 'file' in media_item:
            # Some WordPress instances include the path in 'file' field
            filename = os.path.basename(media_item['file'])
        
        if not filename and source_url:
            # Extract filename from URL
            try:
                filename = os.path.basename(urlparse(source_url).path.split('?')[0])
            except Exception:
                filename = None
        
        if not filename:
            # Fallback to ID if no filename can be determined
            ext = self._guess_extension_from_mime(media_item.get('mime_type', ''))
            filename = f"{media_item['id']}{ext}"
        
        # Create a subfolder based on year/month if available
        subfolder = ""
        if 'date' in media_item:
            try:
                date_str = media_item['date']
                # Handle both formats with and without timezone
                if 'T' in date_str:
                    if date_str.endswith('Z'):
                        date_str = date_str[:-1] + '+00:00'
                    elif '+' not in date_str and '-' not in date_str[10:]:
                        date_str += '+00:00'
                
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                subfolder = f"{date.year}/{date.month:02d}"
                try:
                    (media_dir / subfolder).mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    logger.error(f"Failed to create subfolder {subfolder}: {e}")
                    subfolder = ""  # Reset subfolder if creation fails
            except (ValueError, TypeError) as e:
                logger.debug(f"Error parsing date for media item {media_item.get('id')}: {e}")
                pass
        
        # Full path to save the file
        file_path = media_dir / subfolder / self._sanitize_filename(filename)
        
        # Skip download if file already exists with same size
        if file_path.exists():
            try:
                # If we have file size info in the media item, use it to verify
                if 'filesize' in media_item and file_path.stat().st_size == int(media_item['filesize']):
                    logger.debug(f"Skipping existing file: {file_path} (same size)")
                    return True, 0, 'skipped'
            except (ValueError, OSError):
                pass  # If we can't verify, try to download anyway
        
        # Create parent directory if it doesn't exist
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return False, 0, f"Failed to create directory for media file: {str(e)}"
        
        # Download the file
        try:
            headers = {'User-Agent': f'WordPress-Backup-Tool/{__version__}'}
            
            try:
                # First make a HEAD request to check if the file exists and get its size
                head_response = requests.head(source_url, headers=headers, timeout=10, 
                                             verify=not self.ignore_ssl_errors)
                head_response.raise_for_status()
                
                # Get file size from headers if available
                content_length = int(head_response.headers.get('Content-Length', 0))
                
                # If file already exists and has the same size, skip
                if file_path.exists() and file_path.stat().st_size == content_length and content_length > 0:
                    logger.debug(f"Skipping existing file: {file_path} (same size from headers)")
                    return True, 0, 'skipped'
            except (requests.exceptions.RequestException, ValueError):
                # If HEAD request fails, we'll still try GET
                pass
            
            # Download the file
            response = requests.get(source_url, headers=headers, stream=True, timeout=30,
                                   verify=not self.ignore_ssl_errors)
            response.raise_for_status()
            
            bytes_downloaded = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive new chunks
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
            
            logger.debug(f"Downloaded {bytes_downloaded} bytes to {file_path}")
            return True, bytes_downloaded, ""
            
        except requests.exceptions.RequestException as e:
            return False, 0, f"Download error: {str(e)}"
        except OSError as e:
            return False, 0, f"File system error: {str(e)}"
        except Exception as e:
            return False, 0, f"Unexpected error: {str(e)}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to ensure it's valid on all platforms.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed_file"
            
        # Replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Replace control characters
        filename = ''.join(c if c.isprintable() else '_' for c in filename)
        
        # Ensure filename is not too long (max 255 characters)
        if len(filename) > 255:
            base, ext = os.path.splitext(filename)
            filename = base[:255 - len(ext)] + ext
            
        # Ensure filename is not empty after sanitization
        if not filename or filename.strip() == '':
            filename = "unnamed_file"
            
        return filename
    
    def _guess_extension_from_mime(self, mime_type: str) -> str:
        """
        Guess file extension from MIME type.
        
        Args:
            mime_type: MIME type string
        
        Returns:
            File extension with dot (e.g., '.jpg')
        """
        if not mime_type:
            return '.bin'
            
        mime_to_ext = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'application/pdf': '.pdf',
            'video/mp4': '.mp4',
            'video/quicktime': '.mov',
            'video/x-msvideo': '.avi',
            'video/x-ms-wmv': '.wmv',
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'audio/ogg': '.ogg',
            'audio/midi': '.midi',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'application/x-tar': '.tar',
            'application/x-gzip': '.gz',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'text/plain': '.txt',
            'text/html': '.html',
            'text/css': '.css',
            'text/javascript': '.js',
            'application/json': '.json',
            'application/xml': '.xml',
        }
        return mime_to_ext.get(mime_type.lower(), '.bin')
    
    def _save_backup_info(self) -> None:
        """Save backup information to a JSON file."""
        try:
            if 'end_time' not in self.backup_info:
                self.backup_info['end_time'] = datetime.now().isoformat()
            
            info_file = self.output_dir / "backup_info.json"
            self._save_json_file(info_file, self.backup_info)
        except Exception as e:
            logger.error(f"Failed to save backup info: {e}")
            logger.debug(traceback.format_exc())
    
    def _upload_to_s3(self) -> None:
        """Upload the entire backup to Amazon S3."""
        if not self.s3_client:
            logger.warning("S3 client not initialized, skipping upload")
            return
        
        logger.info(f"Uploading backup to S3 bucket: {self.s3_bucket}")
        
        try:
            # Walk through all files in the backup directory
            uploaded_files = 0
            upload_errors = 0
            total_bytes = 0
            
            # Get list of files to upload
            files_to_upload = []
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    try:
                        local_path = os.path.join(root, file)
                        # Calculate S3 key: remove output_dir from path and add prefix
                        relative_path = os.path.relpath(local_path, self.output_dir)
                        s3_key = os.path.join(self.s3_prefix, relative_path)
                        
                        # Normalize path separators for S3
                        s3_key = s3_key.replace('\\', '/')
                        
                        files_to_upload.append((local_path, s3_key))
                    except Exception as e:
                        logger.error(f"Error preparing file {file} for upload: {e}")
                        upload_errors += 1
            
            # Create a progress tracker
            total_files = len(files_to_upload)
            progress_interval = max(1, total_files // 20)  # Update every ~5%
            
            # Upload files
            for i, (local_path, s3_key) in enumerate(files_to_upload):
                try:
                    file_size = os.path.getsize(local_path)
                    # Only log for large files to reduce verbosity
                    if file_size > 1024 * 1024:  # 1 MB
                        logger.info(f"Uploading {local_path} ({file_size / (1024*1024):.2f} MB) to S3")
                    
                    # Use S3 transfer utility for efficient uploads
                    self.s3_client.upload_file(
                        local_path, 
                        self.s3_bucket, 
                        s3_key,
                        ExtraArgs={'ACL': 'private'}  # Ensure files are private
                    )
                    uploaded_files += 1
                    total_bytes += file_size
                    
                    # Show progress
                    if (i + 1) % progress_interval == 0:
                        progress_pct = ((i + 1) / total_files) * 100
                        total_mb = total_bytes / (1024 * 1024)
                        logger.info(f"S3 upload progress: {i+1}/{total_files} files ({progress_pct:.1f}%), {total_mb:.2f} MB")
                    
                except (NoCredentialsError, ClientError) as e:
                    logger.error(f"S3 upload error for {local_path}: {e}")
                    upload_errors += 1
                except Exception as e:
                    logger.error(f"Unexpected error uploading {local_path} to S3: {e}")
                    logger.debug(traceback.format_exc())
                    upload_errors += 1
            
            # Update backup info with S3 details
            self.backup_info['s3_upload'] = {
                'bucket': self.s3_bucket,
                'prefix': self.s3_prefix,
                'files_uploaded': uploaded_files,
                'upload_errors': upload_errors,
                'total_bytes': total_bytes,
                'total_mb': round(total_bytes / (1024 * 1024), 2)
            }
            
            logger.info(f"S3 upload complete: {uploaded_files} files, "
                       f"{total_bytes / (1024*1024):.2f} MB, {upload_errors} errors")
            
            # Update the backup info file to include S3 upload details
            self._save_backup_info()
            
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def create_archive(self, format: str = 'zip') -> Optional[Path]:
        """
        Create a compressed archive of the backup.
        
        Args:
            format: Archive format ('zip' or 'tar.gz')
        
        Returns:
            Path to the created archive file, or None if creation failed
        """
        base_name = self.output_dir.parent / self.output_dir.name
        
        try:
            if format == 'zip':
                archive_path = Path(f"{base_name}.zip")
                logger.info(f"Creating ZIP archive: {archive_path}")
                shutil.make_archive(str(base_name), 'zip', self.output_dir.parent, self.output_dir.name)
                return archive_path
            elif format == 'tar.gz':
                archive_path = Path(f"{base_name}.tar.gz")
                logger.info(f"Creating TAR.GZ archive: {archive_path}")
                shutil.make_archive(str(base_name), 'gztar', self.output_dir.parent, self.output_dir.name)
                return archive_path
            else:
                raise ValueError(f"Unsupported archive format: {format}")
        except Exception as e:
            logger.error(f"Failed to create archive: {e}")
            logger.debug(traceback.format_exc())
            return None


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=f"WordPress Backup Tool v{__version__} (2025-04-29)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic backup without authentication (public data only):
  python wp_backup.py --url https://example.com
  
  # With optional authentication for more complete backup:
  python wp_backup.py --url https://example.com --username admin --password my_password
  
  # Using environment variables for credentials:
  # export WP_USER=admin
  # export WP_PASSWORD=my_password
  python wp_backup.py --url https://example.com
  
  # Backup specific content types only:
  python wp_backup.py --url https://example.com --content-types posts pages media
  
  # Backup without downloading media files:
  python wp_backup.py --url https://example.com --skip-media
  
  # Backup to a specific directory and create a ZIP archive:
  python wp_backup.py --url https://example.com --output-dir ./my_site_backup --create-archive zip
  
  # Backup to S3:
  # export AWS_ACCESS_KEY_ID=your_access_key
  # export AWS_SECRET_ACCESS_KEY=your_secret_key
  python wp_backup.py --url https://example.com --s3-bucket my-backups --s3-prefix wordpress/mysite
        """
    )
    
    # Required arguments
    parser.add_argument('--url', required=True, help='WordPress site URL')
    
    # Authentication arguments (optional)
    auth_group = parser.add_argument_group('Authentication (Optional)')
    auth_group.add_argument('--username', help='WordPress username (or set WP_USER env var)')
    auth_group.add_argument('--password', help='WordPress password or application password (or set WP_PASSWORD env var)')
    auth_group.add_argument('--auth-type', choices=['basic', 'app_password'], default='app_password',
                         help='Authentication type (default: app_password)')
    auth_group.add_argument('--force-public', action='store_true',
                         help='Force public-only mode even if credentials are provided')
    
    # Output arguments
    output_group = parser.add_argument_group('Output')
    output_group.add_argument('--output-dir', help='Local output directory (default: ./wp_backup_SITENAME_TIMESTAMP)')
    output_group.add_argument('--create-archive', choices=['zip', 'tar.gz'], 
                           help='Create archive after backup')
    
    # Backup options
    backup_group = parser.add_argument_group('Backup Options')
    backup_group.add_argument('--content-types', nargs='+', 
                           help='Content types to backup (default: all public or all with auth)')
    backup_group.add_argument('--max-items', type=int, default=1000,
                           help='Maximum items per content type (default: 1000)')
    backup_group.add_argument('--parallel', type=int, default=5,
                           help='Max parallel downloads for media files (default: 5)')
    backup_group.add_argument('--skip-media', action='store_true',
                           help='Skip downloading media files')
    backup_group.add_argument('--ignore-ssl-errors', action='store_true',
                           help='Ignore SSL certificate errors')
    
    # S3 options
    s3_group = parser.add_argument_group('S3 Options')
    s3_group.add_argument('--s3-bucket', help='S3 bucket for backup (or set S3_BUCKET env var)')
    s3_group.add_argument('--s3-prefix', help='S3 key prefix/folder path (or set S3_PREFIX env var)')
    
    # Other options
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--version', action='version', version=f'WordPress Backup Tool v{__version__}')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Generate a timestamp for the output directory if not specified
    if not args.output_dir:
        try:
            site_name = args.url.replace('https://', '').replace('http://', '').split('/')[0].replace('.', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            args.output_dir = f'./wp_backup_{site_name}_{timestamp}'
        except Exception as e:
            logger.error(f"Error generating output directory name: {e}")
            args.output_dir = f'./wp_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    # Set up signal handlers
    def handle_exit_signal(sig, frame):
        logger.info("Received signal to exit. Cleaning up...")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)
    
    try:
        # Initialize and run backup
        backup = WordPressBackup(
            site_url=args.url,
            username=args.username,
            password=args.password,
            output_dir=args.output_dir,
            s3_bucket=args.s3_bucket,
            s3_prefix=args.s3_prefix,
            content_types=args.content_types,
            max_items_per_type=args.max_items,
            media_max_workers=args.parallel,
            skip_media=args.skip_media,
            auth_type=args.auth_type,
            debug=args.debug,
            ignore_ssl_errors=args.ignore_ssl_errors,
            force_public=args.force_public
        )
        
        # Run the backup
        result = backup.run_backup()
        
        # Create archive if requested
        if args.create_archive:
            archive_path = backup.create_archive(format=args.create_archive)
            if archive_path:
                logger.info(f"Created archive: {archive_path}")
            else:
                logger.error("Failed to create archive")
        
        # Print summary
        auth_status = "authenticated" if backup.is_authenticated else "public (no authentication)"
        logger.info(f"Backup completed successfully to {args.output_dir}")
        logger.info(f"Access mode: {auth_status}")
        logger.info(f"Summary: {len(result.get('stats', {}))} content types backed up")
        
        # Print summary of each content type
        for content_type, stats in result.get('stats', {}).items():
            if isinstance(stats, dict) and 'count' in stats:
                logger.info(f"  - {content_type}: {stats['count']} items")
            elif isinstance(stats, dict) and 'error' in stats:
                logger.info(f"  - {content_type}: Error - {stats['error']}")
        
        # Print media stats if available
        if 'media_files' in result.get('stats', {}):
            media_stats = result['stats']['media_files']
            logger.info(f"  - Media files: {media_stats.get('success', 0)} downloaded, "
                       f"{media_stats.get('failed', 0)} failed, "
                       f"{media_stats.get('bytes_downloaded', 0) / (1024*1024):.2f} MB")
        
        # Print S3 upload stats if available
        if 's3_upload' in result:
            s3_stats = result['s3_upload']
            logger.info(f"  - S3 upload: {s3_stats.get('files_uploaded', 0)} files, "
                       f"{s3_stats.get('total_mb', 0):.2f} MB")
        
        return 0
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Backup interrupted by user")
        return 1
    except WPAPIAuthError as e:
        logger.error(f"Authentication error: {e}")
        logger.info("If you don't need authentication, just omit the --username and --password arguments")
        return 1
    except WPAPIPermissionError:
        logger.error("Permission denied. The user may not have sufficient privileges.")
        return 1
    except WPAPIError as e:
        logger.error(f"WordPress API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        if args.debug:
            logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())