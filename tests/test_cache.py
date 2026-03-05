import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_caching_cache_miss_hit_then_invalidation(monkeypatch):
    """
    Integration test: proves cache-aside + invalidation.
    1) First GET -> cache miss, read from PostgreSQL, store in Redis.
    2) We patch DB (get_post raises). Second GET -> 200 from Redis (no DB).
    3) DELETE invalidates cache. Third GET -> hits DB -> patch raises -> 500.
    """
    import app.repositories.post_repository as repo_module

    client = TestClient(app)

    # Create post
    create_resp = client.post("/posts/", json={"title": "Cached Post", "content": "Body"})
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    # 1) Cache miss: first GET reads from DB and fills Redis
    get1 = client.get(f"/posts/{post_id}")
    assert get1.status_code == 200
    assert get1.json()["title"] == "Cached Post"

    # 2) Break DB: patch get_post to raise. Next GET must come from cache (no DB call).
    def db_raiser(*args, **kwargs):
        raise RuntimeError("DB should not be called when cache hits")

    monkeypatch.setattr(repo_module, "get_post", db_raiser)

    get2 = client.get(f"/posts/{post_id}")
    assert get2.status_code == 200  # From Redis — DB was not called
    assert get2.json()["title"] == "Cached Post"

    # 3) Invalidate cache (DELETE). Keep patch: after GET, handler goes to DB -> get_post raises -> 500.
    del_resp = client.delete(f"/posts/{post_id}")
    assert del_resp.status_code == 204

    get3 = client.get(f"/posts/{post_id}")
    # Cache was invalidated; handler goes to DB; get_post raises -> 500
    assert get3.status_code == 500
