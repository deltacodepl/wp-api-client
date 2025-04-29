"""
WordPress REST API Python Client

A comprehensive Python library for interacting with the WordPress REST API

Created by innerkore, 2025-04-29 09:15:52
"""

__version__ = '0.1.0'

# Import main components
from .client import WPClient
from .auth import BasicAuth, OAuth1, ApplicationPasswordAuth
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
    WPAPIConnectionError
)

__all__ = [
    'WPClient',
    'BasicAuth',
    'OAuth1',
    'ApplicationPasswordAuth',
    'WPAPIError',
    'WPAPIAuthError',
    'WPAPIRequestError',
    'WPAPIRateLimitError',
    'WPAPINotFoundError',
    'WPAPIPermissionError',
    'WPAPIValidationError',
    'WPAPIBadRequestError',
    'WPAPIServerError',
    'WPAPITimeoutError',
    'WPAPIConnectionError',
]