from app import app


def client():
    app.testing = True
    return app.test_client()


def test_health():
    r = client().get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_create_and_list():
    c = client()

    r = c.post("/todos", json={"title": "공부하기"})
    assert r.status_code == 201

    r = c.get("/todos")
    assert any(t["title"] == "공부하기" for t in r.get_json())


def test_title_required():
    r = client().post("/todos", json={})
    assert r.status_code == 400


def test_delete():
    c = client()

    r = c.post("/todos", json={"title": "임시"})
    tid = r.get_json()["id"]

    assert c.delete(f"/todos/{tid}").status_code == 204
    assert c.delete(f"/todos/{tid}").status_code == 404
