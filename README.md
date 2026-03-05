# Blog Cache API

API блога с кешированием постов в Redis (cache-aside) и хранением в PostgreSQL.

## Запуск

```bash
docker-compose up --build
```

- API: http://localhost:8000  
- Документация: http://localhost:8000/docs  

## Переменные окружения (.env)

Скопируйте `.env.example` в `.env` и при необходимости измените значения:

```bash
cp .env.example .env
```

| Переменная     | Описание                    | Пример |
|----------------|-----------------------------|--------|
| `DATABASE_URL` | Подключение к PostgreSQL   | `postgresql://postgres:postgres@db:5432/blog` |
| `REDIS_URL`    | Подключение к Redis         | `redis://redis:6379/0` |
| `CACHE_TTL`    | Время жизни ключа в кеше (сек) | `300` |

## Тесты

Запуск тестов в контейнере (нужны работающие PostgreSQL и Redis):

```bash
docker-compose exec api pytest -q
```

Локально (при запущенных `db` и `redis`):

```bash
pip install -r requirements.txt
pytest -q
```

## Кеширование (cache-aside + invalidation + TTL)

- **Стратегия:** cache-aside. При `GET /posts/{id}` сначала проверяется Redis (ключ `post:{id}`). При промахе данные читаются из PostgreSQL и сохраняются в кеш.
- **TTL:** у каждого ключа задаётся время жизни (по умолчанию 300 сек, настраивается через `CACHE_TTL`), чтобы устаревшие данные не хранились бесконечно.
- **Инвалидация:** при `PUT`/`PATCH`/`DELETE` поста соответствующий ключ в Redis удаляется (`DEL post:{id}`), чтобы при следующем запросе данные снова подтягивались из БД.

## Архитектура

- **api** — HTTP-эндпоинты (REST)
- **services** — бизнес-логика, работа с кешем
- **repositories** — доступ к БД
- **cache** — Redis (ключ `post:{id}`, TTL из `.env`)
- **models** — SQLAlchemy
- **schemas** — Pydantic
