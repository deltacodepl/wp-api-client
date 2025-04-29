# WordPress REST API Python Client

A comprehensive Python library for interacting with the WordPress REST API.

## Features

- Complete support for WordPress REST API endpoints
- Multiple authentication methods (Application Passwords, Basic Auth, OAuth1)
- Intuitive interface for common WordPress operations (posts, pages, media, etc.)
- Support for custom taxonomies and post types
- Custom fields (post meta) management
- Robust error handling with specific exception types
- Full typing support for better IDE integration
- Automatic retries for failed requests
- Comprehensive documentation

## Installation

```bash
pip install wp-api-client
```

## Quick Start

```python
from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth

# Initialize client with Application Password authentication
auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
client = WPClient(base_url="https://your-wordpress-site.com", auth=auth) #auth is optional

# Get all published posts
posts = client.posts.list(status="publish")
for post in posts:
    print(f"Post ID: {post['id']}, Title: {post['title']['rendered']}")

# Create a new post
new_post = client.posts.create(
    title="Hello World",
    content="This is my first post created with the WordPress REST API Python client!",
    status="publish"
)
```

## Authentication Methods

### Application Passwords (Recommended for WordPress 5.6+)

```python
from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth

auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)
```

### Basic Authentication

```python
from wp_api import WPClient
from wp_api.auth import BasicAuth

auth = BasicAuth(username="your_username", password="your_password")
client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)
```

### OAuth1 Authentication

```python
from wp_api import WPClient
from wp_api.auth import OAuth1

auth = OAuth1(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    token="your_token",
    token_secret="your_token_secret"
)
client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)
```

## API Endpoints

The library provides convenient access to various WordPress REST API endpoints:

### Posts

```python
# List posts with filtering
recent_posts = client.posts.list(
    per_page=5,
    status="publish",
    orderby="date",
    order="desc"
)

# Get a specific post
post = client.posts.get(123)

# Create a new post
new_post = client.posts.create(
    title="My New Post",
    content="This is the content of my post.",
    status="publish",
    categories=[5, 7],
    tags=[12, 15]
)

# Update a post
updated_post = client.posts.update(
    123,
    title="Updated Title",
    content="Updated content"
)

# Delete a post
client.posts.delete(123)

# Get post revisions
revisions = client.posts.get_revisions(123)
```

### Pages

```python
# List pages
pages = client.pages.list()

# Get a specific page
page = client.pages.get(45)

# Create a new page
new_page = client.pages.create(
    title="About Us",
    content="<h2>Our Story</h2><p>This is our company story...</p>",
    status="publish"
)

# Update a page
updated_page = client.pages.update(
    45,
    title="Updated About Us",
    content="<h2>Our Updated Story</h2><p>New content here...</p>"
)

# Delete a page
client.pages.delete(45)
```

### Media

```python
# List media items
media_items = client.media.list()

# Get a specific media item
media = client.media.get(67)

# Upload a new image
with open("image.jpg", "rb") as image_file:
    media = client.media.upload(
        image_file,
        file_name="my-image.jpg",
        title="My Image",
        alt_text="Description of my image"
    )

# Update media item
updated_media = client.media.update(
    67,
    title="Updated Image Title",
    alt_text="Updated alternative text"
)

# Delete media item
client.media.delete(67)
```

### Users

```python
# List users
users = client.users.list()

# Get the current user
me = client.users.me()

# Get a specific user
user = client.users.get(2)

# Create a user (requires appropriate permissions)
new_user = client.users.create(
    username="newuser",
    email="new.user@example.com",
    password="secure_password",
    roles=["author"]
)

# Update a user
updated_user = client.users.update(
    2,
    first_name="John",
    last_name="Doe"
)
```

### Categories

```python
# List categories
categories = client.categories.list()

# Get a specific category
category = client.categories.get(5)

# Create a category
new_category = client.categories.create(
    name="Technology",
    description="Tech-related posts"
)

# Update a category
updated_category = client.categories.update(
    5,
    name="Updated Category Name"
)

# Delete a category
client.categories.delete(5)
```

### Tags

```python
# List tags
tags = client.tags.list()

# Get a specific tag
tag = client.tags.get(12)

# Create a tag
new_tag = client.tags.create(
    name="WordPress",
    description="Posts about WordPress"
)

# Update a tag
updated_tag = client.tags.update(
    12,
    description="Updated tag description"
)

# Delete a tag
client.tags.delete(12)
```

### Comments

```python
# List comments
comments = client.comments.list()

# Get comments for a specific post
post_comments = client.comments.list(post=123)

# Get a specific comment
comment = client.comments.get(78)

# Create a comment
new_comment = client.comments.create(
    post=123,
    content="This is a comment on the post.",
    author_name="John Doe",
    author_email="john@example.com"
)

# Update a comment
updated_comment = client.comments.update(
    78,
    content="Updated comment text"
)

# Delete a comment
client.comments.delete(78)
```

### Taxonomies

```python
# Get all taxonomies
taxonomies = client.taxonomies.list()

# Get a specific taxonomy
taxonomy = client.taxonomies.get("category")

# Work with a custom taxonomy
product_categories = client.get_custom_taxonomy("product_cat")
product_terms = product_categories.list()
```

### Custom Post Types

```python
# Get custom post type handler
products = client.get_custom_post_type("product")

# List products
all_products = products.list(per_page=20)

# Get a specific product
product = products.get(123)

# Create a product
new_product = products.create(
    title="New Product",
    status="publish",
    regular_price="19.99"  # Custom field
)

# Get custom fields for products
product_meta = products.get_meta()
```

### Custom Fields (Post Meta)

```python
# Get custom fields handler for posts
post_meta = client.get_custom_fields("posts")

# Get all meta for a post
all_meta = post_meta.get_all(123)

# Get a specific meta value
meta_value = post_meta.get(123, "meta_key")

# Create a new meta field
new_meta = post_meta.create(123, "meta_key", "meta_value")

# Update or create a meta field
meta = post_meta.update_or_create(123, "meta_key", "new_value")

# Delete a meta field
post_meta.delete(123, meta_id=456)
```

### Settings

```python
# Get all settings
settings = client.settings.get()

# Update settings
updated_settings = client.settings.update(
    title="My Site Title",
    description="My site tagline"
)
```

### Block Patterns (WordPress 5.8+)

```python
# Get all block patterns
patterns = client.block_patterns.list()

# Get block pattern categories
pattern_categories = client.block_patterns.get_categories()
```

## Error Handling

The library provides specific exception types for different error scenarios:

```python
from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth
from wp_api.exceptions import (
    WPAPIError,             # Base exception for all WP API errors
    WPAPIAuthError,         # Authentication errors
    WPAPIRequestError,      # General request errors
    WPAPIRateLimitError,    # Rate limiting (429)
    WPAPINotFoundError,     # Resource not found (404)
    WPAPIPermissionError,   # Permission denied (401, 403)
    WPAPIValidationError,   # Validation errors (400)
    WPAPIBadRequestError,   # Bad request errors (400)
    WPAPIServerError,       # Server errors (500+)
    WPAPITimeoutError,      # Request timeout
    WPAPIConnectionError    # Connection error
)

try:
    auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
    client = WPClient(base_url="https://your-wordpress-site.com", auth=auth)
    
    # Try to access a resource
    post = client.posts.get(999999)  # Non-existent post ID
    
except WPAPIAuthError as e:
    print(f"Authentication error: {e}")
    
except WPAPIPermissionError as e:
    print(f"Permission denied: {e}")
    
except WPAPINotFoundError as e:
    print(f"Resource not found: {e}")
    
except WPAPIRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    
except WPAPIServerError as e:
    print(f"Server error: {e}")
    print(f"Status code: {e.status_code}")
    
except WPAPIValidationError as e:
    print(f"Validation error: {e}")
    print(f"Error details: {e.error_data}")
    
except WPAPIRequestError as e:
    print(f"Request error: {e}")
    print(f"Status code: {e.status_code}")
    
except WPAPIError as e:
    print(f"WordPress API error: {e}")
```

The library also maps specific WordPress REST API error codes to appropriate exception types.

## Advanced Usage

### Configuring Request Retries

```python
# Configure client with retry settings
client = WPClient(
    base_url="https://your-wordpress-site.com",
    auth=auth,
    timeout=30,              # 30 second timeout
    retry_count=3,           # Retry failed requests 3 times
    retry_backoff_factor=0.5 # Increase wait time between retries
)
```

### Discovering API Endpoints

```python
# Discover available endpoints
endpoints = client.discover_endpoints()
```

### Custom Request Parameters

All endpoint methods accept additional parameters that will be passed to the API request:

```python
# Pass custom parameters to the API
posts = client.posts.list(
    status="publish",
    custom_param="value"
)
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/username/wp-api-client.git
cd wp-api-client

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=wp_api tests/

# Run tests across multiple Python versions
tox
```

### Building Documentation

```bash
# Build documentation
make docs
```

### Building and Publishing

```bash
# Create distribution
make dist

# Publish to PyPI
make release
```

## API Reference

For a complete API reference, see the detailed [API Documentation](https://wp-api-client.readthedocs.io/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- WordPress REST API documentation: https://developer.wordpress.org/rest-api/
- The requests library: https://requests.readthedocs.io/