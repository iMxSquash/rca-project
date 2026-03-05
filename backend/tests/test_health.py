"""Tests for the /health endpoint."""

from unittest.mock import MagicMock, patch


class TestHealthEndpoint:
    """Test suite for the health check endpoint."""

    def test_health_returns_200(self, client):
        """GET /health should return HTTP 200."""
        with patch("app.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            response = client.get("/health")

        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        """GET /health should return status 'ok' when DB is reachable."""
        with patch("app.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            response = client.get("/health")
            data = response.get_json()

        assert data["status"] == "ok"
        assert data["database"] == "ok"

    def test_health_contains_timestamp(self, client):
        """GET /health should include an ISO timestamp."""
        with patch("app.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            response = client.get("/health")
            data = response.get_json()

        assert "timestamp" in data

    def test_health_degraded_when_db_fails(self, client):
        """GET /health should return 'degraded' when DB connection fails."""
        with patch("app.get_db", side_effect=Exception("DB down")):
            response = client.get("/health")
            data = response.get_json()

        assert response.status_code == 200
        assert data["status"] == "degraded"
        assert data["database"] == "error"

    def test_health_response_is_json(self, client):
        """GET /health should return application/json content type."""
        with patch("app.get_db") as mock_get_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_db.return_value = mock_conn

            response = client.get("/health")

        assert response.content_type == "application/json"
