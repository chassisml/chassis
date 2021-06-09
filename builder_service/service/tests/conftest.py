#!/usr/bin/env python
# -*- coding utf-8 -*-

import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app({"TESTING": True})

    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
