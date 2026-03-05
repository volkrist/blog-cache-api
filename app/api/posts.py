from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.post_schema import PostCreate, PostUpdate, PostResponse
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostResponse])
def list_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return post_service.get_posts(db, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=dict)
def read_post(post_id: int, db: Session = Depends(get_db)):
    result = post_service.get_post_cached(db, post_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@router.post("/", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return post_service.create_post(db, post)


@router.put("/{post_id}", response_model=PostResponse)
def update_post_full(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    result = post_service.update_post(db, post_id, PostUpdate(title=post.title, content=post.content))
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@router.patch("/{post_id}", response_model=PostResponse)
def update_post_partial(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    result = post_service.update_post(db, post_id, post)
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    if not post_service.delete_post(db, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return None
