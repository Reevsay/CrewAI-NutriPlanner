"""
Pytest configuration and shared fixtures
"""
import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables"""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "True"
    os.environ["LOG_LEVEL"] = "DEBUG"
    # Use dummy API keys for testing
    os.environ["OPENAI_API_KEY"] = "test-key-123"
    yield
    # Cleanup after tests if needed