import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def get_redis():
    return redis.from_url(REDIS_URL, decode_responses=True)


def cache_get(key: str):
    r = get_redis()
    data = r.get(key)
    if data:
        return json.loads(data)
    return None


def cache_set(key: str, value: dict, ttl: int = 300):
    r = get_redis()
    r.setex(key, ttl, json.dumps(value, default=str))
