"""Tests for the /api/search endpoint."""

from unittest.mock import MagicMock, patch


class TestSearchTasks:
    """Test suite for the search endpoint."""

    def test_search_returns_200(self, client):
        """GET /api/search?q=test should return HTTP 200."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/search?q=test")

        assert response.status_code == 200

    def test_search_returns_list(self, client):
        """GET /api/search should return a JSON array."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/search?q=anything")
            data = response.get_json()

        assert isinstance(data, list)

    def test_search_returns_matching_tasks(self, client, sample_task):
        """GET /api/search should return tasks matching the query."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [sample_task]
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/search?q=Test")
            data = response.get_json()

        assert len(data) == 1
        assert data[0]["title"] == "Test Task"

    def test_search_uses_ilike_query(self, client):
        """GET /api/search should use ILIKE for case-insensitive matching."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            client.get("/api/search?q=hello")

        query = mock_cursor.execute.call_args[0][0]
        assert "ILIKE" in query

    def test_search_logs_to_redis(self, client):
        """GET /api/search should push the query to Redis search_history."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_r = MagicMock()
            mock_get_redis.return_value = mock_r

            client.get("/api/search?q=logged")

        mock_r.lpush.assert_called_once()
        assert mock_r.lpush.call_args[0][0] == "search_history"

    def test_search_trims_history(self, client):
        """GET /api/search should trim search_history to 100 entries."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_r = MagicMock()
            mock_get_redis.return_value = mock_r

            client.get("/api/search?q=trim")

        mock_r.ltrim.assert_called_once_with("search_history", 0, 99)

    def test_search_empty_query(self, client):
        """GET /api/search with empty query should still return 200."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/search?q=")

        assert response.status_code == 200
