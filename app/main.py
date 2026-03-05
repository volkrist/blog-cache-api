from fastapi import FastAPI
from app.db import init_db
from app.api.posts import router as posts_router

app = FastAPI(title="Blog Cache API")
app.include_router(posts_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
