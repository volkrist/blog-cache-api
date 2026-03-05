from sqlalchemy.orm import Session
from app.repositories import post_repository
from app.cache.redis_cache import cache_get, cache_set, cache_delete, cache_key
from app.cache.redis_cache import CACHE_TTL
from app.schemas.post_schema import PostCreate, PostUpdate, PostResponse


def get_post_cached(db: Session, post_id: int):
    key = cache_key(post_id)
    cached = cache_get(key)
    if cached:
        return cached
    post = post_repository.get_post(db, post_id)
    if post:
        data = PostResponse.model_validate(post).model_dump()
        cache_set(key, data, CACHE_TTL)
        return data
    return None


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return post_repository.get_posts(db, skip=skip, limit=limit)


def create_post(db: Session, post: PostCreate):
    return post_repository.create_post(db, post)


def update_post(db: Session, post_id: int, post: PostUpdate):
    result = post_repository.update_post(db, post_id, post)
    if result is not None:
        cache_delete(cache_key(post_id))
    return result


def delete_post(db: Session, post_id: int):
    ok = post_repository.delete_post(db, post_id)
    if ok:
        cache_delete(cache_key(post_id))
    return ok
