from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics

import os
import sys
import time

# ✅ make sure python can find model.py
sys.path.append("/app")

from model import db, Todo   # 👈 IMPORTANT (model, not models)

app = Flask(__name__)

metrics = PrometheusMetrics(app)
@app.route("/")
def home():
    return "Backend is running", 200

@app.route("/favicon.ico")
def favicon():
    return "", 204


# Custom app info metric
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

# initialize DB
db.init_app(app)

# ✅ wait for postgres and create tables safely
for i in range(10):
    try:
        with app.app_context():
            db.create_all()
        break
    except Exception as e:
        print("Database not ready, retrying...", e)
        time.sleep(3)

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

#@app.route("/api/todos", methods=["GET", "POST"])
#@app.route("/todos", methods=["GET", "POST"])
#def todos():
#    # ---------- POST ----------
#    if request.method == "POST":
#        data = request.get_json(silent=True)
#
#        if not data or "title" not in data:
#            return jsonify({"error": "title is required"}), 400
#
#        todo = Todo(title=data["title"])
#        db.session.add(todo)
#        db.session.commit()
#
#        return jsonify({"message": "Todo added"}), 201
#
#    # ---------- GET ----------
#    title = request.args.get("title")
#
#    if title:
#        # ❌ SQL Injection vulnerability (FOR CodeQL TEST ONLY)
#        result = db.session.execute(
#            f"SELECT * FROM todo WHERE title = '{title}'"
#        )
#        return jsonify([dict(row) for row in result])
#
#    todos = Todo.query.all()
#    return jsonify([t.to_dict() for t in todos])



@app.route("/health")
def health():
    return jsonify({"status": "UP"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
