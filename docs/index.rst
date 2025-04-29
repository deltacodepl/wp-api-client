WordPress REST API Python Client
===============================

.. image:: https://img.shields.io/pypi/v/wp-api-client.svg
        :target: https://pypi.python.org/pypi/wp-api-client

.. image:: https://readthedocs.org/projects/wp-api-client/badge/?version=latest
        :target: https://wp-api-client.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

A comprehensive Python library for interacting with the WordPress REST API.

Features
--------

* Complete support for WordPress REST API endpoints
* Multiple authentication methods (Application Passwords, Basic Auth, OAuth1)
* Intuitive interface for common WordPress operations (posts, pages, media, etc.)
* Support for custom taxonomies and post types
* Custom fields (post meta) management
* Robust error handling with specific exception types
* Full typing support for better IDE integration
* Automatic retries for failed requests

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   usage
   examples
   deployment

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   modules/client
   modules/auth
   modules/exceptions
   modules/endpoints

.. toctree::
   :maxdepth: 1
   :caption: Development:
   
   contributing
   authors
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`