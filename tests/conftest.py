"""
Test configuration and fixtures for the Mergington High School Activities API.

This module provides pytest fixtures that follow the AAA (Arrange-Act-Assert) pattern
by setting up fresh test data and isolated application state for each test.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture: Provides a TestClient connected to the FastAPI application.
    
    This allows tests to make HTTP requests to the API endpoints without
    needing to run the server externally.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Fixture: Provides a deep-copied activities database for test isolation.
    
    This fixture ensures each test gets a fresh copy of the activities data,
    preventing tests from affecting each other. Uses monkeypatch to replace
    the module-level activities dict.
    
    Returns:
        dict: A deep copy of the original activities database
    """
    # ARRANGE: Create a fresh copy of activities for this test
    test_activities = deepcopy(activities)
    monkeypatch.setattr("src.app.activities", test_activities)
    return test_activities
