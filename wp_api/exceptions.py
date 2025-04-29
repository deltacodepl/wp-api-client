"""
Exceptions for WordPress REST API client
"""

class WPAPIError(Exception):
    """Base class for WordPress REST API errors"""
    pass


class WPAPIAuthError(WPAPIError):
    """Authentication error with the WordPress REST API"""
    pass


class WPAPIRequestError(WPAPIError):
    """Error making a request to the WordPress REST API"""
    
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.error_data = None
        
        # Try to parse error details from response
        if response is not None:
            try:
                self.error_data = response.json()
            except (ValueError, AttributeError):
                pass


class WPAPIRateLimitError(WPAPIRequestError):
    """Rate limiting error from the WordPress REST API"""
    pass


class WPAPINotFoundError(WPAPIRequestError):
    """Resource not found error from the WordPress REST API"""
    pass


class WPAPIPermissionError(WPAPIRequestError):
    """Permission denied error from the WordPress REST API"""
    pass


class WPAPIValidationError(WPAPIRequestError):
    """Validation error from the WordPress REST API"""
    pass


class WPAPIBadRequestError(WPAPIRequestError):
    """Bad request error from the WordPress REST API"""
    pass


class WPAPIServerError(WPAPIRequestError):
    """Server error from the WordPress REST API"""
    pass


class WPAPITimeoutError(WPAPIRequestError):
    """Timeout error when connecting to the WordPress REST API"""
    pass


class WPAPIConnectionError(WPAPIRequestError):
    """Connection error when connecting to the WordPress REST API"""
    pass


# Map of WordPress REST API error codes to exception classes
# Based on common WordPress REST API error codes
ERROR_CODE_MAP = {
    "rest_no_route": WPAPINotFoundError,
    "rest_post_invalid_id": WPAPINotFoundError,
    "rest_page_invalid_id": WPAPINotFoundError,
    "rest_user_invalid_id": WPAPINotFoundError,
    "rest_comment_invalid_id": WPAPINotFoundError,
    "rest_media_invalid_id": WPAPINotFoundError,
    "rest_term_invalid_id": WPAPINotFoundError,
    "rest_taxonomy_invalid": WPAPINotFoundError,
    "rest_invalid_param": WPAPIValidationError,
    "rest_forbidden": WPAPIPermissionError,
    "rest_cannot_create": WPAPIPermissionError,
    "rest_cannot_update": WPAPIPermissionError,
    "rest_cannot_delete": WPAPIPermissionError,
    "rest_cannot_read": WPAPIPermissionError,
    "rest_invalid_user": WPAPIAuthError,
    "rest_cookie_invalid_nonce": WPAPIAuthError,
    "rest_authentication_required": WPAPIAuthError,
}