#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get version without importing the package
with open(os.path.join(here, "wp_api", "__init__.py"), encoding="utf-8") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in wp_api/__init__.py")

setup(
    name="wp-api-client",
    version=version,
    description="Python client for the WordPress REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/innerkorehq/wp-api-client",
    author="Gagan (innerkore)",
    author_email="gagan@innerkore.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="wordpress, api, rest, wp-api",
    packages=find_packages(include=["wp_api", "wp_api.*"]),
    python_requires=">=3.6",
    install_requires=["requests>=2.25.0"],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=20.8b1",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "isort>=5.0.0",
            "tox>=3.20.0",
            "sphinx>=3.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinx-autodoc-typehints>=1.12.0",
            "twine>=3.3.0",
            "build>=0.5.0",
            "wheel>=0.36.2",
        ],
        "docs": [
            "sphinx>=3.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "sphinx-autodoc-typehints>=1.12.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/innerkorehq/wp-api-client/issues",
        "Source": "https://github.com/innerkorehq/wp-api-client",
        "Documentation": "https://wp-api-client.readthedocs.io/",
    },
)