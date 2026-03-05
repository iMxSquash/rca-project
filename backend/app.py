"""Flask REST API for the Task Manager application."""

import json
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request, g, Response
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import redis as redis_lib

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://taskuser:taskpass@db:5432/taskdb")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

def get_db() -> psycopg2.extensions.connection:
    """Return the current request's database connection, creating one if needed."""
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL)
        g.db.autocommit = True
    return g.db

def get_redis() -> redis_lib.Redis:  # type: ignore[type-arg]
    """Return the current request's Redis client, creating one if needed."""
    if "redis" not in g:
        g.redis = redis_lib.from_url(REDIS_URL)
    return g.redis

@app.teardown_appcontext
def close_db(exception: BaseException | None) -> None:
    """Close the database connection at the end of the request context."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.before_request
def log_request() -> None:
    """Log incoming request method and path, and record the start time."""
    try:
        g.start_time = datetime.now()
        app.logger.info(f"{request.method} {request.path}")
    except Exception:
        pass

@app.after_request
def after_request(response: Response) -> Response:
    """Log the response status code and request duration after each request."""
    try:
        duration = datetime.now() - g.start_time
        app.logger.info(f"{request.method} {request.path} -> {response.status_code} ({duration.total_seconds():.3f}s)")
    except Exception:
        pass
    return response

@app.route("/health")
def health() -> Response:
    """Health check endpoint. Returns service status and database connectivity."""
    result = {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT 1")
        cur.close()
        result["database"] = "ok"
    except Exception:
        result["database"] = "error"
        result["status"] = "degraded"
    return jsonify(result)

@app.route("/api/tasks", methods=["GET"])
def list_tasks() -> Response:
    """List all tasks with optional filtering by status or creation date."""
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    status = request.args.get("status")
    today_only = request.args.get("today")
    query = "SELECT * FROM tasks"
    conditions = []
    params = []
    if status:
        conditions.append("is_active = true" if status == "active" else "is_active = false")
    if today_only:
        conditions.append("DATE(created_at) = DATE(%s)")
        params.append(datetime.now())
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"
    cur.execute(query, params)
    tasks = cur.fetchall()
    result = []
    for t in tasks:
        result.append({
            "id": t["id"], "title": t["title"], "description": t["description"],
            "is_active": t["is_active"],
            "created_at": t["created_at"].isoformat() if t["created_at"] else None,
            "updated_at": t["updated_at"].isoformat() if t["updated_at"] else None,
        })
    return jsonify(result)

@app.route("/api/tasks", methods=["POST"])
def create_task() -> Response | tuple[Response, int]:
    """Create a new task. Requires a unique title in the JSON body."""
    data = request.get_json()
    if not data or not data.get("title"):
        app.logger.warning("POST /api/tasks - 400 Title is required")
        return jsonify({"error": "Title is required"}), 400
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO tasks (title, description, is_active, created_at, updated_at) VALUES (%s, %s, %s, %s, %s) RETURNING *",
            (data["title"], data.get("description", ""), True, datetime.now(timezone.utc), datetime.now(timezone.utc))
        )
        task = cur.fetchone()
    except psycopg2.errors.UniqueViolation:
        db.rollback()
        app.logger.warning(f"POST /api/tasks - 409 Duplicate title: {data.get('title')}")
        return jsonify({"error": "A task with this title already exists"}), 409
    r = get_redis()
    r.delete("stats")
    return jsonify({
        "id": task["id"], "title": task["title"], "description": task["description"],
        "is_active": task["is_active"], "created_at": task["created_at"].isoformat(),
        "updated_at": task["updated_at"].isoformat(),
    }), 201

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id: int) -> Response | tuple[Response, int]:
    """Retrieve a single task by its ID. Returns 404 if not found."""
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    if not task:
        app.logger.warning(f"GET /api/tasks/{task_id} - 404 Not found")
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": task["id"], "title": task["title"], "description": task["description"],
        "is_active": task["is_active"],
        "created_at": task["created_at"].isoformat() if task["created_at"] else None,
        "updated_at": task["updated_at"].isoformat() if task["updated_at"] else None,
    })

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id: int) -> Response | tuple[Response, int]:
    """Update an existing task by ID. Returns 404 if the task does not exist."""
    data = request.get_json()
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    if not task:
        app.logger.warning(f"PUT /api/tasks/{task_id} - 404 Not found")
        return jsonify({"error": "Not found"}), 404
    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    is_active = data.get("is_active", task["is_active"])
    cur.execute(
        "UPDATE tasks SET title = %s, description = %s, is_active = %s, updated_at = %s WHERE id = %s RETURNING *",
        (title, description, is_active, datetime.now(timezone.utc), task_id)
    )
    updated = cur.fetchone()
    r = get_redis()
    r.delete("stats")
    return jsonify({
        "id": updated["id"], "title": updated["title"], "description": updated["description"],
        "is_active": updated["is_active"], "created_at": updated["created_at"].isoformat(),
        "updated_at": updated["updated_at"].isoformat(),
    })

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int) -> tuple[str, int]:
    """Delete a task by ID and invalidate the stats cache."""
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    r = get_redis()
    r.delete("stats")
    return "", 204

@app.route("/api/search", methods=["GET"])
def search_tasks() -> Response:
    """Search tasks by title or description using ILIKE and log the query to Redis."""
    q = request.args.get("q", "")
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE title ILIKE %s OR description ILIKE %s", (f"%{q}%", f"%{q}%"))
    results = cur.fetchall()
    r = get_redis()
    r.lpush("search_history", json.dumps({"query": q, "results_count": len(results), "timestamp": datetime.now().isoformat()}))
    r.ltrim("search_history", 0, 99)
    serialized = []
    for t in results:
        serialized.append({
            "id": t["id"], "title": t["title"], "description": t["description"],
            "is_active": t["is_active"],
            "created_at": t["created_at"].isoformat() if t["created_at"] else None,
        })
    return jsonify(serialized)

@app.route("/api/stats", methods=["GET"])
def get_stats() -> Response:
    """Return task statistics (total, active, done) with Redis caching."""
    r = get_redis()
    cached = r.get("stats")
    if cached:
        return jsonify(json.loads(cached))
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE is_active = true) as active, COUNT(*) FILTER (WHERE is_active = false) as done FROM tasks")
    stats = cur.fetchone()
    r.setex("stats", 300, json.dumps(dict(stats)))
    return jsonify(dict(stats))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
