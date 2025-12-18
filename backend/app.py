from flask import Flask, request, jsonify
import os
import sys
import time

# ✅ make sure python can find model.py
sys.path.append("/app")

from model import db, Todo   # 👈 IMPORTANT (model, not models)

app = Flask(__name__)

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

@app.route("/todos", methods=["GET", "POST"])
def todos():
    if request.method == "POST":
        data = request.json
        todo = Todo(title=data["title"])
        db.session.add(todo)
        db.session.commit()
        return jsonify({"message": "Todo added"}), 201

    todos = Todo.query.all()
    return jsonify([t.to_dict() for t in todos])

@app.route("/health")
def health():
    return jsonify({"status": "UP"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
