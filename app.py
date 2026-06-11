from flask import Flask, jsonify, request, abort
import psycopg

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "todo_db",
    "user": "todo_user",
    "password": "todo_pass",
}


def get_conn():
    return psycopg.connect(**DB_CONFIG)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/todos")
def list_todos():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, done FROM todos ORDER BY id"
            )

            rows = cur.fetchall()

    todos = [
        {
            "id": row[0],
            "title": row[1],
            "done": row[2],
        }
        for row in rows
    ]

    return jsonify(todos)


@app.post("/todos")
def add_todo():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()

    if not title:
        abort(400, "title is required")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO todos (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title, False),
            )

            row = cur.fetchone()

        conn.commit()

    todo = {
        "id": row[0],
        "title": row[1],
        "done": row[2],
    }

    return jsonify(todo), 201


@app.patch("/todos/<int:tid>")
def toggle(tid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE todos
                SET done = NOT done
                WHERE id = %s
                RETURNING id, title, done
                """,
                (tid,),
            )

            row = cur.fetchone()

        conn.commit()

    if row is None:
        abort(404)

    todo = {
        "id": row[0],
        "title": row[1],
        "done": row[2],
    }

    return jsonify(todo)


@app.delete("/todos/<int:tid>")
def delete(tid):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM todos WHERE id = %s",
                (tid,),
            )

            deleted = cur.rowcount

        conn.commit()

    return ("", 204) if deleted else ("", 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)