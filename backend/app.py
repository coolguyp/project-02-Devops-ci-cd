from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import os
import sys
import time

# make sure python can find model.py
sys.path.append("/app")

from model import db, Todo

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# -------------------------------------------------
# ✅ SECURE CONFIGURATION
# -------------------------------------------------

# Load secrets from environment variables
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "change-this-in-prod")

@app.route("/")
def home():
    return "Backend is running", 200

@app.route("/favicon.ico")
def favicon():
    return "", 204


metrics.info(
    "todo_app_info",
    "ToDo application info",
    version="1.0.0"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/tododb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# wait for postgres
for i in range(10):
    try:
        with app.app_context():
            db.create_all()
        break
    except Exception as e:
        print("Database not ready, retrying...", e)
        time.sleep(3)

# -------------------------------------------------
# ✅ SAFE TODOS API
# -------------------------------------------------
@app.route("/api/todos", methods=["GET", "POST"])
@app.route("/todos", methods=["GET", "POST"])
def todos():
    if request.method == "POST":
        data = request.get_json(silent=True)

        if not data or "title" not in data:
            return jsonify({"error": "title is required"}), 400

        # Basic input validation
        title = str(data["title"]).strip()

        if len(title) > 255:
            return jsonify({"error": "title too long"}), 400

        todo = Todo(title=title)
        db.session.add(todo)
        db.session.commit()
        return jsonify({"message": "Todo added"}), 201

    todos = Todo.query.all()
    return jsonify([t.to_dict() for t in todos])

# -------------------------------------------------
# ✅ SAFE SEARCH API (NO SQL INJECTION)
# -------------------------------------------------
@app.route("/search")
def safe_search():
    title = request.args.get("title", "")

    # Use ORM filter instead of raw SQL
    results = Todo.query.filter(Todo.title.like(f"%{title}%")).all()

    return jsonify([t.to_dict() for t in results])

# -------------------------------------------------
# ✅ SAFE FILE READ (NO PATH TRAVERSAL)
# -------------------------------------------------
@app.route("/files")
def safe_file_read():
    filename = request.args.get("file")

    if not filename:
        return jsonify({"error": "file parameter required"}), 400

    # Allow only files inside a safe directory
    SAFE_DIR = "/app/safe_files"

    safe_path = os.path.join(SAFE_DIR, filename)
    safe_path = os.path.realpath(safe_path)

    if not safe_path.startswith(os.path.realpath(SAFE_DIR)):
        return jsonify({"error": "Invalid file path"}), 403

    if not os.path.exists(safe_path):
        return jsonify({"error": "File not found"}), 404

    with open(safe_path, "r") as f:
        content = f.read()

    return jsonify({"content": content})

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "UP"})

# -------------------------------------------------
# ✅ PRODUCTION SAFE MODE
# -------------------------------------------------
if __name__ == "__main__":
    # Debug OFF for security
    app.run(host="0.0.0.0", port=5000, debug=False)
