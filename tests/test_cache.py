import pytest
from httpx import AsyncClient
from app.main import app
import app.repositories.post_repository as repo_module


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_cache_aside_and_invalidation(monkeypatch):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1) Create
        r = await client.post("/posts/", json={"title": "t1", "content": "c1"})
        assert r.status_code == 201
        created = r.json()
        post_id = created["id"]

        # 2) First GET -> cache miss, DB -> Redis SET
        r1 = await client.get(f"/posts/{post_id}")
        assert r1.status_code == 200
        assert r1.json()["id"] == post_id

        # Подменяем репозиторий только для проверки cache-hit
        def _boom(*args, **kwargs):
            raise RuntimeError("DB should not be called on cache hit")

        original_get_post = repo_module.get_post
        monkeypatch.setattr(repo_module, "get_post", _boom)

        # 3) Second GET -> must be from Redis (БД не вызывается)
        r2 = await client.get(f"/posts/{post_id}")
        assert r2.status_code == 200
        assert r2.json()["title"] == "t1"

        # Возвращаем оригинальную функцию
        monkeypatch.setattr(repo_module, "get_post", original_get_post)

        # 4) PUT -> invalidation (DEL key)
        r3 = await client.put(f"/posts/{post_id}", json={"title": "t2"})
        assert r3.status_code == 200
        assert r3.json()["title"] == "t2"

        # 5) После инвалидации GET идёт в БД и возвращает обновлённый пост
        r4 = await client.get(f"/posts/{post_id}")
        assert r4.status_code == 200
        assert r4.json()["title"] == "t2"

        # 6) DELETE
        r5 = await client.delete(f"/posts/{post_id}")
        assert r5.status_code == 204

        # 7) После удаления GET -> 404
        r6 = await client.get(f"/posts/{post_id}")
        assert r6.status_code == 404
