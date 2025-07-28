#!/usr/bin/env python3
"""
Main entry point for medlitanno package when called as module
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main()) 