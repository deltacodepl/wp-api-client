# WordPress REST API Python Client Examples

This document provides examples of how to use the WordPress REST API Python client library.

## Basic Setup

```python
from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth

# Using Application Passwords (recommended)
auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
client = WPClient(base_url="https://example.com", auth=auth)
```

## Working with Posts

### List Posts

```python
# Get all published posts
posts = client.posts.list(status="publish")

# Get posts with filtering
recent_posts = client.posts.list(
    per_page=5,
    status="publish",
    orderby="date",
    order="desc",
    author=12
)

# Get posts by category
posts_in_category = client.posts.list(
    categories=5,
    per_page=10
)

# Search posts
search_results = client.posts.list(
    search="wordpress",
    per_page=20
)
```

### Get a Specific Post

```python
# Get a post by ID
post = client.posts.get(123)

# Print post title and content
print(f"Title: {post['title']['rendered']}")
print(f"Content: {post['content']['rendered']}")
```

### Create a Post

```python
# Create a draft post
draft_post = client.posts.create(
    title="My Draft Post",
    content="This is a draft post content.",
    status="draft"
)

# Create a published post with categories and tags
published_post = client.posts.create(
    title="My Published Post",
    content="This is the content of my published post.",
    excerpt="A short excerpt for the post.",
    status="publish",
    categories=[5, 7],
    tags=[12, 15],
    featured_media=42
)
```

### Update a Post

```python
# Update a post
updated_post = client.posts.update(
    123,
    title="Updated Title",
    content="This content has been updated."
)

# Change a post's status from draft to publish
published = client.posts.update(
    123,
    status="publish"
)
```

### Delete a Post

```python
# Delete a post (moves to trash by default)
deleted_post = client.posts.delete(123)

# Delete a post permanently
permanently_deleted = client.posts.delete(123, {"force": True})
```

### Working with Post Revisions

```python
# Get all revisions of a post
revisions = client.posts.get_revisions(123)

# Get a specific revision
revision = client.posts.get_revision(123, 456)
```

## Working with Media

### List Media

```python
# Get all media
media_items = client.media.list()

# Filter by media type
images = client.media.list(media_type="image")
```

### Upload Media

```python
# Upload an image file
with open("image.jpg", "rb") as img_file:
    uploaded_image = client.media.upload(
        img_file,
        title="My Uploaded Image",
        alt_text="An image description for accessibility",
        caption="This is the image caption"
    )
```

### Update Media

```python
# Update media metadata
updated_media = client.media.update(
    456,
    title="New Title for Image",
    alt_text="Updated alt text",
    caption="Updated caption"
)
```

### Delete Media

```python
# Delete a media item
client.media.delete(456)
```

## Working with Pages

```python
# List pages
pages = client.pages.list(status="publish")

# Create a page
new_page = client.pages.create(
    title="About Us",
    content="<h2>Our Story</h2><p>This is our company story...</p>",
    status="publish"
)

# Update a page
updated_page = client.pages.update(
    789,
    content="<h2>Our Updated Story</h2><p>New content here...</p>"
)

# Get a specific page
page = client.pages.get(789)

# Delete a page
client.pages.delete(789)
```

## Working with Users

```python
# List users
users = client.users.list()

# Get current user (requires authentication)
current_user = client.users.me()

# Get a specific user
user = client.users.get(42)

# Create a user (requires appropriate permissions)
new_user = client.users.create(
    username="newuser",
    email="user@example.com",
    password="secure_password",
    name="New User",
    roles=["author"]
)

# Update a user
updated_user = client.users.update(
    42,
    first_name="Updated",
    last_name="Name"
)
```

## Working with Taxonomies (Categories and Tags)

### Categories

```python
# List categories
categories = client.categories.list()

# Create a category
new_category = client.categories.create(
    name="Technology",
    description="Tech-related posts"
)

# Update a category
updated_category = client.categories.update(
    15,
    name="Updated Category Name",
    description="Updated description"
)

# Get a specific category
category = client.categories.get(15)

# Delete a category
client.categories.delete(15)
```

### Tags

```python
# List tags
tags = client.tags.list()

# Create a tag
new_tag = client.tags.create(
    name="WordPress",
    description="Posts about WordPress"
)

# Update a tag
updated_tag = client.tags.update(
    27,
    description="Updated tag description"
)

# Get a specific tag
tag = client.tags.get(27)

# Delete a tag
client.tags.delete(27)
```

## Working with Comments

```python
# List comments
comments = client.comments.list()

# Get approved comments for a specific post
post_comments = client.comments.list(post=123, status="approve")

# Create a comment on a post
new_comment = client.comments.create(
    post=123,
    content="This is my comment on the post.",
    author_name="John Doe",
    author_email="john@example.com"
)

# Reply to a comment
reply = client.comments.create(
    post=123,
    content="This is a reply to the comment.",
    parent=456
)

# Update a comment
updated_comment = client.comments.update(
    456,
    content="Updated comment text"
)

# Delete a comment
client.comments.delete(456)
```

## Working with Custom Fields (Post Meta)

```python
# Access custom fields for posts
post_meta = client.get_custom_fields("posts")

# Get all meta for a post
all_meta = post_meta.get_all(123)

# Get a specific meta value
meta_value = post_meta.get(123, "meta_key")

# Create a new meta field
new_meta = post_meta.create(123, "meta_key", "meta_value")

# Update an existing meta field
updated_meta = post_meta.update(123, meta_id=456, meta_value="new_value")

# Update or create a meta field (handles both cases)
meta = post_meta.update_or_create(123, "meta_key", "meta_value")

# Delete a meta field
post_meta.delete(123, meta_id=456)
```

## Working with Custom Taxonomies

```python
# Get a custom taxonomy handler
product_categories = client.get_custom_taxonomy("product_cat")

# List terms in the custom taxonomy
terms = product_categories.list()

# Create a new term
new_term = product_categories.create(
    name="Electronics",
    description="Electronic products"
)

# Update a term
updated_term = product_categories.update(
    78,
    description="Updated description for electronics"
)

# Delete a term
product_categories.delete(78)
```

## Error Handling

```python
from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth
from wp_api.exceptions import WPAPIError, WPAPIAuthError, WPAPINotFoundError, WPAPIPermissionError

try:
    auth = ApplicationPasswordAuth(username="your_username", app_password="your_app_password")
    client = WPClient(base_url="https://example.com", auth=auth)
    
    # Try to access something that requires permissions
    posts = client.posts.list(status="draft")
    
except WPAPIAuthError as e:
    print(f"Authentication error: {e}")
    
except WPAPIPermissionError as e:
    print(f"Permission denied: {e}")
    
except WPAPINotFoundError as e:
    print(f"Resource not found: {e}")
    
except WPAPIError as e:
    print(f"WordPress API error: {e}")
    
except Exception as e:
    print(f"General error: {e}")
```

## Working with WordPress REST API Settings

```python
# Get all settings
settings = client.settings.get()

# Print some common settings
print(f"Site title: {settings.get('title')}")
print(f"Tag line: {settings.get('description')}")
print(f"Posts per page: {settings.get('posts_per_page')}")

# Update settings (requires admin privileges)
updated_settings = client.settings.update(
    title="New Site Title",
    description="New tagline for the site"
)
```

## Discovering API Endpoints

```python
# Discover available API endpoints
endpoints = client.discover_endpoints()

# Print available routes
for route, data in endpoints.get('routes', {}).items():
    print(f"Route: {route}")
    print(f"Methods: {', '.join(data.get('methods', []))}")
    print("---")
```