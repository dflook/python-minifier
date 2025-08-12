"""Pytest configuration and fixtures for python-minifier tests."""
import os

# Set default environment variable to preserve existing test behavior
# Tests can explicitly unset this if they need to test size-based behavior
os.environ.setdefault('PYMINIFY_FORCE_BEST_EFFORT', '1')