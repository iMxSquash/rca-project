"""Tests for the /api/tasks CRUD endpoints."""

from unittest.mock import MagicMock, patch


class TestListTasks:
    """Test suite for GET /api/tasks."""

    def test_list_tasks_returns_200(self, client):
        """GET /api/tasks should return HTTP 200."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/tasks")

        assert response.status_code == 200

    def test_list_tasks_returns_list(self, client):
        """GET /api/tasks should return a JSON array."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/tasks")
            data = response.get_json()

        assert isinstance(data, list)

    def test_list_tasks_returns_task_data(self, client, sample_task):
        """GET /api/tasks should return serialized task objects."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [sample_task]
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/tasks")
            data = response.get_json()

        assert len(data) == 1
        assert data[0]["title"] == "Test Task"
        assert data[0]["is_active"] is True

    def test_list_tasks_filter_active(self, client):
        """GET /api/tasks?status=active should query active tasks."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.get("/api/tasks?status=active")

        assert response.status_code == 200
        mock_cursor.execute.assert_called_once()
        query = mock_cursor.execute.call_args[0][0]
        assert "is_active = true" in query


class TestCreateTask:
    """Test suite for POST /api/tasks."""

    def test_create_task_returns_201(self, client, sample_task):
        """POST /api/tasks should return HTTP 201 on success."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = sample_task
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.post("/api/tasks",
                                   json={"title": "New Task", "description": "Desc"})

        assert response.status_code == 201

    def test_create_task_returns_task(self, client, sample_task):
        """POST /api/tasks should return the created task data."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = sample_task
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.post("/api/tasks", json={"title": "New Task"})
            data = response.get_json()

        assert data["title"] == "Test Task"
        assert data["is_active"] is True

    def test_create_task_missing_title_returns_400(self, client):
        """POST /api/tasks with no title should return HTTP 400."""
        response = client.post("/api/tasks", json={"description": "No title"})

        assert response.status_code == 400
        assert "Title is required" in response.get_json()["error"]

    def test_create_task_empty_body_returns_400(self, client):
        """POST /api/tasks with empty body should return HTTP 400."""
        response = client.post("/api/tasks",
                               data="",
                               content_type="application/json")

        assert response.status_code == 400

    def test_create_task_invalidates_stats_cache(self, client, sample_task):
        """POST /api/tasks should delete the 'stats' Redis key."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = sample_task
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_r = MagicMock()
            mock_get_redis.return_value = mock_r

            client.post("/api/tasks", json={"title": "New Task"})

        mock_r.delete.assert_called_with("stats")


class TestGetTask:
    """Test suite for GET /api/tasks/<id>."""

    def test_get_task_returns_200(self, client, sample_task):
        """GET /api/tasks/1 should return HTTP 200 when task exists."""
        with patch("app.get_db") as mock_get_db:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = sample_task
            mock_get_db.return_value.cursor.return_value = mock_cursor

            response = client.get("/api/tasks/1")

        assert response.status_code == 200
        assert response.get_json()["id"] == 1

    def test_get_task_not_found_returns_404(self, client):
        """GET /api/tasks/999 should return HTTP 404 when task is missing."""
        with patch("app.get_db") as mock_get_db:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_get_db.return_value.cursor.return_value = mock_cursor

            response = client.get("/api/tasks/999")

        assert response.status_code == 404
        assert "Not found" in response.get_json()["error"]


class TestUpdateTask:
    """Test suite for PUT /api/tasks/<id>."""

    def test_update_task_returns_200(self, client, sample_task):
        """PUT /api/tasks/1 should return HTTP 200 on success."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [sample_task, sample_task]
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.put("/api/tasks/1",
                                  json={"title": "Updated"})

        assert response.status_code == 200

    def test_update_task_not_found_returns_404(self, client):
        """PUT /api/tasks/999 should return HTTP 404 when task is missing."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.put("/api/tasks/999", json={"title": "X"})

        assert response.status_code == 404


class TestDeleteTask:
    """Test suite for DELETE /api/tasks/<id>."""

    def test_delete_task_returns_204(self, client):
        """DELETE /api/tasks/1 should return HTTP 204."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_get_redis.return_value = MagicMock()

            response = client.delete("/api/tasks/1")

        assert response.status_code == 204

    def test_delete_task_invalidates_stats_cache(self, client):
        """DELETE /api/tasks/1 should delete the 'stats' Redis key."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_r = MagicMock()
            mock_get_redis.return_value = mock_r

            client.delete("/api/tasks/1")

        mock_r.delete.assert_called_with("stats")


class TestGetStats:
    """Test suite for GET /api/stats."""

    def test_stats_returns_200(self, client):
        """GET /api/stats should return HTTP 200."""
        with patch("app.get_db") as mock_get_db, \
             patch("app.get_redis") as mock_get_redis:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = {"total": 3, "active": 2, "done": 1}
            mock_get_db.return_value.cursor.return_value = mock_cursor
            mock_r = MagicMock()
            mock_r.get.return_value = None
            mock_get_redis.return_value = mock_r

            response = client.get("/api/stats")

        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 3
        assert data["active"] == 2
        assert data["done"] == 1

    def test_stats_uses_cache(self, client):
        """GET /api/stats should return cached data if available."""
        import json

        with patch("app.get_redis") as mock_get_redis:
            mock_r = MagicMock()
            mock_r.get.return_value = json.dumps({"total": 5, "active": 3, "done": 2})
            mock_get_redis.return_value = mock_r

            response = client.get("/api/stats")
            data = response.get_json()

        assert data["total"] == 5
