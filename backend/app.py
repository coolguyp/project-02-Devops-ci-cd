from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics

import os
import sys
import time
import subprocess   # ❌ for command injection demo

# ✅ make sure python can find model.py
sys.path.append("/app")

from model import db, Todo

app = Flask(__name__)

metrics = PrometheusMetrics(app)

# -------------------------------------------------
# ❌ HARD-CODED SECRET (FOR SCAN TEST ONLY)
# -------------------------------------------------
API_SECRET_KEY = "my-super-secret-password"   # SonarQube will flag this

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
# NORMAL TODOS API
# -------------------------------------------------
@app.route("/api/todos", methods=["GET", "POST"])
@app.route("/todos", methods=["GET", "POST"])
def todos():
    if request.method == "POST":
        data = request.get_json(silent=True)

        if not data or "title" not in data:
            return jsonify({"error": "title is required"}), 400

        todo = Todo(title=data["title"])
        db.session.add(todo)
        db.session.commit()
        return jsonify({"message": "Todo added"}), 201

    todos = Todo.query.all()
    return jsonify([t.to_dict() for t in todos])

# -------------------------------------------------
# ❌ SQL INJECTION VULNERABILITY
# -------------------------------------------------
@app.route("/vuln/sql")
def sql_injection_demo():
    title = request.args.get("title")

    # ❌ INTENTIONAL SQL INJECTION
    query = f"SELECT * FROM todo WHERE title = '{title}'"
    result = db.session.execute(query)

    return jsonify([dict(row) for row in result])

# -------------------------------------------------
# ❌ COMMAND INJECTION VULNERABILITY
# -------------------------------------------------
@app.route("/vuln/cmd")
def command_injection_demo():
    cmd = request.args.get("cmd")

    # ❌ INTENTIONAL COMMAND INJECTION
    output = subprocess.getoutput(cmd)

    return jsonify({"output": output})

# -------------------------------------------------
# ❌ PATH TRAVERSAL
# -------------------------------------------------
@app.route("/vuln/file")
def file_read_demo():
    filename = request.args.get("file")

    # ❌ INTENTIONAL PATH TRAVERSAL
    with open(filename, "r") as f:
        content = f.read()

    return jsonify({"content": content})

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "UP"})

# -------------------------------------------------
# ❌ INSECURE DEBUG MODE
# -------------------------------------------------
if __name__ == "__main__":
    # ❌ Debug mode exposes stack traces
    app.run(host="0.0.0.0", port=5000, debug=True)
