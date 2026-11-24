"""分页与搜索的测试。"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create(client: TestClient, title: str) -> dict:
    response = client.post("/notes", json={"title": title})
    assert response.status_code == 201
    return response.json()


def test_pagination_limit(client: TestClient) -> None:
    """limit=2 只返回两条。"""
    for title in ["A", "B", "C", "D", "E"]:
        _create(client, title)

    response = client.get("/notes?limit=2")

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["A", "B"]


def test_pagination_skip(client: TestClient) -> None:
    """skip=2 从第三条开始。"""
    for title in ["A", "B", "C", "D"]:
        _create(client, title)

    response = client.get("/notes?skip=2&limit=2")

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["C", "D"]


def test_pagination_default_limit(client: TestClient) -> None:
    """不传 limit 时默认最多返回 20 条。"""
    for index in range(25):
        _create(client, f"笔记{index}")

    response = client.get("/notes")

    assert response.status_code == 200
    assert len(response.json()) == 20


def test_invalid_limit_returns_422(client: TestClient) -> None:
    """limit=0 或超过 100 都应该被校验拦截。"""
    assert client.get("/notes?limit=0").status_code == 422
    assert client.get("/notes?limit=101").status_code == 422


def test_search_matches_title(client: TestClient) -> None:
    """搜索只返回标题包含关键词的记录。"""
    _create(client, "FastAPI 入门")
    _create(client, "Python 基础")
    _create(client, "fastapi 进阶")

    response = client.get("/notes/search?q=fastapi")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert titles == ["FastAPI 入门", "fastapi 进阶"]


def test_search_no_hit_returns_empty(client: TestClient) -> None:
    """搜不到返回空列表。"""
    _create(client, "随便一条")

    response = client.get("/notes/search?q=不存在的词")

    assert response.status_code == 200
    assert response.json() == []


def test_search_requires_keyword(client: TestClient) -> None:
    """q 为空或缺失返回 422。"""
    assert client.get("/notes/search?q=").status_code == 422
    assert client.get("/notes/search").status_code == 422
