"""
WordPress REST API Client
Core client implementation for making requests to the WordPress REST API
"""

import requests
import json
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin
from .exceptions import (
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
    WPAPIConnectionError,
    ERROR_CODE_MAP
)


class WPClient:
    """
    WordPress REST API Client
    
    The main client class for interacting with the WordPress REST API.
    """
    
    def __init__(
        self, 
        base_url: str,
        auth=None,
        timeout: int = 30,
        user_agent: str = "Python WordPress REST API Client",
        verify_ssl: bool = True,
        retry_count: int = 0,
        retry_backoff_factor: float = 0.1
    ):
        """
        Initialize the WordPress REST API client
        
        Args:
            base_url (str): The base URL of the WordPress site (e.g., https://example.com)
            auth: Authentication method (BasicAuth, OAuth1, or ApplicationPasswordAuth)
            timeout (int): Request timeout in seconds
            user_agent (str): User agent string for the requests
            verify_ssl (bool): Whether to verify SSL certificates
            retry_count (int): Number of retries for failed requests
            retry_backoff_factor (float): Backoff factor for retries
        """
        if not base_url.endswith('/'):
            base_url += '/'
            
        self.base_url = urljoin(base_url, 'wp-json/wp/v2/')
        self.root_url = urljoin(base_url, 'wp-json/')
        self.auth = auth
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_backoff_factor = retry_backoff_factor
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        self.session.verify = verify_ssl
        
        # Cache for discovered endpoints
        self._endpoints_cache = None
        
        # Cache for custom post type handlers
        self._custom_post_types = {}
        
        # Add authentication if provided
        if self.auth:
            try:
                self.auth.authenticate(self.session)
            except Exception as e:
                raise WPAPIAuthError(f"Failed to authenticate: {str(e)}") from e
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Union[Dict, List]:
        """
        Make a GET request to the API
        
        Args:
            endpoint (str): API endpoint (relative to base URL)
            params (dict, optional): URL parameters to include
            
        Returns:
            Response data (dict or list)
        """
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Dict, params: Optional[Dict] = None) -> Dict:
        """
        Make a POST request to the API
        
        Args:
            endpoint (str): API endpoint (relative to base URL)
            data (dict): Data to send in the request body
            params (dict, optional): URL parameters to include
            
        Returns:
            Response data (dict)
        """
        return self._request("POST", endpoint, data=data, params=params)
    
    def put(self, endpoint: str, data: Dict, params: Optional[Dict] = None) -> Dict:
        """
        Make a PUT request to the API
        
        Args:
            endpoint (str): API endpoint (relative to base URL)
            data (dict): Data to send in the request body
            params (dict, optional): URL parameters to include
            
        Returns:
            Response data (dict)
        """
        return self._request("PUT", endpoint, data=data, params=params)
    
    def delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a DELETE request to the API
        
        Args:
            endpoint (str): API endpoint (relative to base URL)
            params (dict, optional): URL parameters to include
            
        Returns:
            Response data (dict)
        """
        return self._request("DELETE", endpoint, params=params)
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None, 
        params: Optional[Dict] = None
    ) -> Union[Dict, List]:
        """
        Make a request to the API
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint (relative to base URL)
            data (dict, optional): Data to send in the request body
            params (dict, optional): URL parameters to include
            
        Returns:
            Response data (dict or list)
        """
        url = urljoin(self.base_url, endpoint)
        request_kwargs = {
            "params": params,
            "timeout": self.timeout,
        }
        
        if data is not None:
            request_kwargs["data"] = json.dumps(data)
            
        # Retry logic
        retries = self.retry_count
        
        while True:
            try:
                response = self.session.request(method, url, **request_kwargs)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                # Handle API errors
                self._handle_request_error(e)
                
            except requests.exceptions.Timeout as e:
                if retries <= 0:
                    raise WPAPITimeoutError(
                        f"Request timed out after {self.timeout} seconds",
                        response=getattr(e, 'response', None)
                    ) from e
                retries -= 1
                
            except requests.exceptions.ConnectionError as e:
                if retries <= 0:
                    raise WPAPIConnectionError(
                        f"Failed to connect to {url}",
                        response=getattr(e, 'response', None)
                    ) from e
                retries -= 1
                
            except requests.exceptions.RequestException as e:
                raise WPAPIRequestError(
                    f"Request failed: {str(e)}",
                    response=getattr(e, 'response', None)
                ) from e
                
            except json.JSONDecodeError as e:
                raise WPAPIRequestError(f"Failed to parse response as JSON: {str(e)}") from e
    
    def _handle_request_error(self, error: requests.exceptions.HTTPError):
        """
        Handle HTTP errors and raise appropriate exceptions
        
        Args:
            error: The HTTP error
            
        Raises:
            WPAPIRateLimitError: For rate limiting errors (429)
            WPAPINotFoundError: For not found errors (404)
            WPAPIPermissionError: For permission errors (401, 403)
            WPAPIValidationError: For validation errors (400)
            WPAPIServerError: For server errors (500+)
            WPAPIRequestError: For other HTTP errors
        """
        response = error.response
        status_code = response.status_code
        error_msg = f"HTTP Error: {status_code}"
        error_data = None
        
        # Try to parse error details from response
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                if 'message' in error_data:
                    error_msg = f"{error_msg} - {error_data['message']}"
                
                # Check for WordPress specific error code
                if 'code' in error_data and error_data['code'] in ERROR_CODE_MAP:
                    exception_class = ERROR_CODE_MAP[error_data['code']]
                    raise exception_class(
                        error_msg, 
                        status_code=status_code,
                        response=response
                    ) from error
        except (ValueError, json.JSONDecodeError):
            pass
            
        # Handle based on status code if no specific error code was found
        if status_code == 429:
            raise WPAPIRateLimitError(error_msg, status_code=status_code, response=response) from error
        elif status_code == 404:
            raise WPAPINotFoundError(error_msg, status_code=status_code, response=response) from error
        elif status_code in (401, 403):
            raise WPAPIPermissionError(error_msg, status_code=status_code, response=response) from error
        elif status_code == 400:
            raise WPAPIBadRequestError(error_msg, status_code=status_code, response=response) from error
        elif 400 <= status_code < 500:
            raise WPAPIValidationError(error_msg, status_code=status_code, response=response) from error
        elif status_code >= 500:
            raise WPAPIServerError(error_msg, status_code=status_code, response=response) from error
        else:
            raise WPAPIRequestError(error_msg, status_code=status_code, response=response) from error
    
    def discover_endpoints(self) -> Dict:
        """
        Discover available endpoints from the WordPress REST API
        
        Returns:
            Dictionary of available routes/endpoints
        """
        if self._endpoints_cache is None:
            try:
                response = self.session.get(self.root_url, timeout=self.timeout)
                response.raise_for_status()
                self._endpoints_cache = response.json()
            except requests.exceptions.RequestException as e:
                raise WPAPIRequestError(
                    f"Failed to discover endpoints: {str(e)}",
                    response=getattr(e, 'response', None)
                ) from e
            except json.JSONDecodeError as e:
                raise WPAPIRequestError(f"Failed to parse response as JSON: {str(e)}") from e
        return self._endpoints_cache
    
    def get_custom_taxonomy(self, taxonomy: str):
        """
        Get a custom taxonomy endpoint handler
        
        Args:
            taxonomy: Taxonomy slug (e.g., 'category', 'post_tag', or custom taxonomy)
            
        Returns:
            Terms endpoint handler for the specified taxonomy
        """
        from .endpoints.taxonomies import Terms
        return Terms(self, taxonomy)
    
    def get_custom_fields(self, post_type: str = "posts"):
        """
        Get a custom fields endpoint handler for a specific post type
        
        Args:
            post_type: Post type (posts, pages, or custom post type)
            
        Returns:
            CustomFields endpoint handler for the specified post type
        """
        from .endpoints.custom_fields import CustomFields
        return CustomFields(self, post_type)
    
    def get_custom_post_type(self, post_type: str):
        """
        Get a custom post type endpoint handler
        
        Args:
            post_type: Custom post type slug (e.g., 'product', 'portfolio', etc.)
            
        Returns:
            CustomPostType endpoint handler for the specified post type
        """
        # Check if we already have a handler for this post type
        if post_type not in self._custom_post_types:
            from .endpoints.custom_post_types import CustomPostType
            self._custom_post_types[post_type] = CustomPostType(self, post_type)
        
        return self._custom_post_types[post_type]

    # Shortcut properties for common endpoints
    @property
    def posts(self):
        """Access Posts API endpoints"""
        from .endpoints.posts import Posts
        return Posts(self)
    
    @property
    def pages(self):
        """Access Pages API endpoints"""
        from .endpoints.pages import Pages
        return Pages(self)
    
    @property
    def users(self):
        """Access Users API endpoints"""
        from .endpoints.users import Users
        return Users(self)
    
    @property
    def media(self):
        """Access Media API endpoints"""
        from .endpoints.media import Media
        return Media(self)
    
    @property
    def categories(self):
        """Access Categories API endpoints"""
        from .endpoints.categories import Categories
        return Categories(self)
    
    @property
    def tags(self):
        """Access Tags API endpoints"""
        from .endpoints.tags import Tags
        return Tags(self)
    
    @property
    def comments(self):
        """Access Comments API endpoints"""
        from .endpoints.comments import Comments
        return Comments(self)
    
    @property
    def taxonomies(self):
        """Access Taxonomies API endpoints"""
        from .endpoints.taxonomies import Taxonomies
        return Taxonomies(self)
    
    @property
    def settings(self):
        """Access Settings API endpoints"""
        from .endpoints.settings import Settings
        return Settings(self)
        
    @property
    def block_patterns(self):
        """Access Block Patterns API endpoints (WordPress 5.8+)"""
        from .endpoints.block_patterns import BlockPatterns
        return BlockPatterns(self)