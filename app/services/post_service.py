from sqlalchemy.orm import Session
from app.repositories import post_repository
from app.cache.redis_cache import cache_get, cache_set
from app.schemas.post_schema import PostCreate, PostResponse

CACHE_TTL = 300


def get_post_cached(db: Session, post_id: int):
    cache_key = f"post:{post_id}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    post = post_repository.get_post(db, post_id)
    if post:
        data = PostResponse.model_validate(post).model_dump()
        cache_set(cache_key, data, CACHE_TTL)
        return data
    return None


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return post_repository.get_posts(db, skip=skip, limit=limit)


def create_post(db: Session, post: PostCreate):
    return post_repository.create_post(db, post)
