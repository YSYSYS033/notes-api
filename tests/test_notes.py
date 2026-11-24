"""笔记 CRUD 的测试。"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_note(client: TestClient) -> None:
    """创建成功返回 201 和完整字段。"""
    response = client.post("/notes", json={"title": "第一条", "content": "内容"})

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "第一条"
    assert data["content"] == "内容"
    assert "created_at" in data
    assert data["updated_at"] is not None


def test_list_notes(client: TestClient) -> None:
    """列表按创建顺序返回。"""
    client.post("/notes", json={"title": "A"})
    client.post("/notes", json={"title": "B"})

    response = client.get("/notes")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert titles == ["A", "B"]


def test_get_note(client: TestClient) -> None:
    """按 id 查询。"""
    created = client.post("/notes", json={"title": "可查询"}).json()

    response = client.get(f"/notes/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "可查询"


def test_get_missing_note_returns_404(client: TestClient) -> None:
    """查不到的 id 返回 404。"""
    response = client.get("/notes/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "笔记不存在"


def test_update_note(client: TestClient) -> None:
    """patch 只改传了的字段。"""
    created = client.post("/notes", json={"title": "旧标题", "content": "保留内容"}).json()

    response = client.patch(f"/notes/{created['id']}", json={"title": "新标题"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "新标题"
    assert data["content"] == "保留内容"


def test_update_missing_note_returns_404(client: TestClient) -> None:
    response = client.patch("/notes/999", json={"title": "x"})

    assert response.status_code == 404


def test_delete_note(client: TestClient) -> None:
    """删除后返回 204，再查就是 404。"""
    created = client.post("/notes", json={"title": "要删的"}).json()

    response = client.delete(f"/notes/{created['id']}")
    assert response.status_code == 204

    assert client.get(f"/notes/{created['id']}").status_code == 404


def test_delete_missing_note_returns_404(client: TestClient) -> None:
    response = client.delete("/notes/999")

    assert response.status_code == 404


def test_create_note_rejects_empty_title(client: TestClient) -> None:
    """空标题返回 422。"""
    response = client.post("/notes", json={"title": ""})

    assert response.status_code == 422


def test_create_note_rejects_too_long_title(client: TestClient) -> None:
    """标题超过 200 字返回 422。"""
    response = client.post("/notes", json={"title": "x" * 201})

    assert response.status_code == 422


def test_create_note_rejects_missing_title(client: TestClient) -> None:
    """缺 title 字段返回 422。"""
    response = client.post("/notes", json={"content": "没有标题"})

    assert response.status_code == 422
