import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))


def get_redis():
    return redis.from_url(REDIS_URL, decode_responses=True)


def cache_key(post_id: int) -> str:
    return f"post:{post_id}"


def cache_get(key: str):
    r = get_redis()
    data = r.get(key)
    if data:
        return json.loads(data)
    return None


def cache_set(key: str, value: dict, ttl: int = CACHE_TTL):
    r = get_redis()
    r.setex(key, ttl, json.dumps(value, default=str))


def cache_delete(key: str):
    r = get_redis()
    r.delete(key)
