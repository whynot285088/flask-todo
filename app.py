from flask import Flask, jsonify, request, abort

app = Flask(__name__)

_todos = []
_next_id = 1


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/todos")
def list_todos():
    return jsonify(_todos)


@app.post("/todos")
def add_todo():
    global _next_id

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()

    if not title:
        abort(400, "title is required")

    todo = {
        "id": _next_id,
        "title": title,
        "done": False
    }

    _todos.append(todo)
    _next_id += 1

    return jsonify(todo), 201


@app.patch("/todos/<int:tid>")
def toggle(tid):
    for t in _todos:
        if t["id"] == tid:
            t["done"] = not t["done"]
            return jsonify(t)

    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    app.run(host="0.0.0.0", port=5000)
