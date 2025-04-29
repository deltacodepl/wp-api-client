"""
WordPress REST API Endpoints

Collection of endpoint classes for the WordPress REST API
"""

from .base import BaseEndpoint
from .posts import Posts
from .pages import Pages
from .users import Users
from .media import Media
from .categories import Categories
from .tags import Tags
from .comments import Comments
from .settings import Settings
from .taxonomies import Taxonomies, Terms
from .custom_fields import CustomFields
from .custom_post_types import CustomPostType
from .block_patterns import BlockPatterns

__all__ = [
    'BaseEndpoint',
    'Posts',
    'Pages',
    'Users',
    'Media',
    'Categories',
    'Tags',
    'Comments',
    'Settings',
    'Taxonomies',
    'Terms',
    'CustomFields',
    'CustomPostType',
    'BlockPatterns'
]