"""Shared pytest fixtures for backend tests."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture()
def mock_db():
    """Create a mock database connection with a mock cursor."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture()
def mock_redis():
    """Create a mock Redis client."""
    return MagicMock()


@pytest.fixture()
def app(mock_db, mock_redis):
    """Create a Flask test app with mocked DB and Redis."""
    mock_conn, _ = mock_db

    with patch("app.psycopg2") as mock_psycopg2, \
         patch("app.redis_lib") as mock_redis_lib:
        mock_psycopg2.connect.return_value = mock_conn
        mock_psycopg2.extras = MagicMock()
        mock_psycopg2.extras.RealDictCursor = "RealDictCursor"
        mock_psycopg2.errors.UniqueViolation = type("UniqueViolation", (Exception,), {})
        mock_psycopg2.extensions.connection = type(mock_conn)
        mock_redis_lib.from_url.return_value = mock_redis

        from app import app as flask_app
        flask_app.config["TESTING"] = True
        yield flask_app


@pytest.fixture()
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture()
def sample_task():
    """Return a sample task dict as returned by the database."""
    now = datetime(2026, 3, 5, 12, 0, 0, tzinfo=timezone.utc)
    return {
        "id": 1,
        "title": "Test Task",
        "description": "A test task",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
