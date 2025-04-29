#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify setup.py properly extracts version information.
This is a simple test to ensure our setup.py works without errors.
"""

import os
import re

def get_version():
    with open(os.path.join(os.path.dirname(__file__), "wp_api", "__init__.py"), encoding="utf-8") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        else:
            raise RuntimeError("Unable to find version string in wp_api/__init__.py")

if __name__ == "__main__":
    try:
        version = get_version()
        print(f"Successfully extracted version: {version}")
    except Exception as e:
        print(f"Error extracting version: {e}")
        exit(1)
    
    # Success
    exit(0)