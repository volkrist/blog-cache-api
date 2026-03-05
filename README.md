# Blog Cache API

FastAPI-приложение с кэшированием постов в Redis и хранением в PostgreSQL.

## Архитектура

- **api** — HTTP-эндпоинты
- **services** — бизнес-логика, работа с кэшем
- **repositories** — доступ к БД
- **cache** — Redis
- **models** — SQLAlchemy-модели
- **schemas** — Pydantic-схемы

## Запуск

```bash
docker-compose up --build
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Локальная разработка

```bash
cp .env.example .env
pip install -r requirements.txt
# Запустить PostgreSQL и Redis (docker-compose up db redis)
uvicorn app.main:app --reload
```

## Тесты

```bash
pytest
```
