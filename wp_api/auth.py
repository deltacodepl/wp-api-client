"""
Authentication methods for the WordPress REST API
"""

import base64
import requests
from typing import Dict, Optional
import urllib.parse
import hmac
import hashlib
import time
import random
import string
import uuid


class BasicAuth:
    """
    Basic Authentication for WordPress REST API
    
    Note: This method is not recommended for production use unless over HTTPS
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize Basic Authentication
        
        Args:
            username (str): WordPress username
            password (str): WordPress password
        """
        self.username = username
        self.password = password
    
    def authenticate(self, session: requests.Session) -> None:
        """
        Add authentication to session
        
        Args:
            session (requests.Session): The session to authenticate
        """
        auth_string = f"{self.username}:{self.password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        session.headers.update({"Authorization": f"Basic {encoded_auth}"})


class ApplicationPasswordAuth:
    """
    Application Password Authentication for WordPress REST API
    
    This is the recommended authentication method for WordPress 5.6+
    """
    
    def __init__(self, username: str, app_password: str):
        """
        Initialize Application Password Authentication
        
        Args:
            username (str): WordPress username
            app_password (str): Application password generated in WordPress admin
        """
        self.username = username
        self.app_password = app_password
    
    def authenticate(self, session: requests.Session) -> None:
        """
        Add authentication to session
        
        Args:
            session (requests.Session): The session to authenticate
        """
        auth_string = f"{self.username}:{self.app_password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        session.headers.update({"Authorization": f"Basic {encoded_auth}"})


class OAuth1:
    """
    OAuth1 Authentication for WordPress REST API
    """
    
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        token: Optional[str] = None,
        token_secret: Optional[str] = None
    ):
        """
        Initialize OAuth1 Authentication
        
        Args:
            consumer_key (str): OAuth consumer key
            consumer_secret (str): OAuth consumer secret
            token (str, optional): OAuth token
            token_secret (str, optional): OAuth token secret
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret
        
    def authenticate(self, session: requests.Session) -> None:
        """
        Add authentication to session
        
        Args:
            session (requests.Session): The session to authenticate
        """
        # Patch session to use OAuth1
        original_request = session.request
        
        def oauth_request(method, url, **kwargs):
            # Add OAuth1 headers
            oauth_params = self._get_oauth_params(method, url, kwargs.get('params', {}))
            headers = kwargs.get('headers', {})
            headers['Authorization'] = self._build_auth_header(oauth_params)
            kwargs['headers'] = headers
            return original_request(method, url, **kwargs)
        
        session.request = oauth_request

    def _get_oauth_params(self, method: str, url: str, params: Dict) -> Dict:
        """Generate OAuth parameters"""
        oauth_params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_nonce': uuid.uuid4().hex,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_version': '1.0',
        }
        
        if self.token:
            oauth_params['oauth_token'] = self.token
            
        # Generate signature
        base_string = self._get_base_string(method, url, {**params, **oauth_params})
        signing_key = self._get_signing_key()
        signature = self._get_signature(base_string, signing_key)
        oauth_params['oauth_signature'] = signature
        
        return oauth_params
        
    def _get_base_string(self, method: str, url: str, params: Dict) -> str:
        """Generate OAuth base string"""
        # Sort parameters by key
        sorted_params = sorted(params.items())
        
        # Encode parameters
        encoded_params = urllib.parse.urlencode(sorted_params)
        
        # Create base string
        base_parts = [
            method.upper(),
            urllib.parse.quote(url, safe=''),
            urllib.parse.quote(encoded_params, safe='')
        ]
        
        return '&'.join(base_parts)
        
    def _get_signing_key(self) -> str:
        """Generate OAuth signing key"""
        consumer_secret = urllib.parse.quote(self.consumer_secret, safe='')
        if self.token_secret:
            token_secret = urllib.parse.quote(self.token_secret, safe='')
            return f"{consumer_secret}&{token_secret}"
        return f"{consumer_secret}&"
        
    def _get_signature(self, base_string: str, signing_key: str) -> str:
        """Generate OAuth signature"""
        signature = hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha1
        )
        return base64.b64encode(signature.digest()).decode()
        
    def _build_auth_header(self, oauth_params: Dict) -> str:
        """Build OAuth Authorization header"""
        auth_header_parts = []
        
        for key, value in sorted(oauth_params.items()):
            auth_header_parts.append(f'{urllib.parse.quote(key, safe="")}="{urllib.parse.quote(value, safe="")}"')
            
        return f"OAuth {', '.join(auth_header_parts)}"