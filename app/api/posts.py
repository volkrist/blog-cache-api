from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.post_schema import PostCreate, PostResponse
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/{post_id}", response_model=dict)
def read_post(post_id: int, db: Session = Depends(get_db)):
    result = post_service.get_post_cached(db, post_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@router.get("/", response_model=list[PostResponse])
def list_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return post_service.get_posts(db, skip=skip, limit=limit)


@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return post_service.create_post(db, post)
