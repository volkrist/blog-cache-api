# Blog Cache API

Простой backend-сервис блога на FastAPI с хранением данных в PostgreSQL и кешированием популярных запросов в Redis.

Проект демонстрирует реализацию:

- REST API
- CRUD операций
- cache-aside стратегии кеширования
- инвалидации кеша
- интеграционных тестов
- контейнеризации через Docker

Это тестовое задание для позиции Junior Python Backend Developer.

## Стек технологий

- Python 3.11
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Pytest
- Docker / Docker Compose

## Архитектура

Проект разделён на слои:

```
app
├─ api            # HTTP роуты (REST API)
├─ services       # бизнес-логика
├─ repositories   # доступ к базе данных
├─ cache          # работа с Redis
├─ models         # SQLAlchemy модели
├─ schemas        # Pydantic схемы
└─ main.py        # точка входа FastAPI
```

Поток обработки запроса:

```
Client
  ↓
FastAPI (api)
  ↓
Service layer
  ↓
Cache (Redis)
  ↓
Repository
  ↓
PostgreSQL
```

## Запуск проекта

Требуется установленный Docker.

Запуск сервисов:

```bash
docker-compose up --build
```

После запуска:

- **API** — http://localhost:8000
- **Swagger документация** — http://localhost:8000/docs

## Проверка работы

Поднять стек:

```bash
docker-compose up -d --build
```

Запустить тесты:

```bash
docker-compose exec api pytest -q
```

## Переменные окружения

Создайте `.env` на основе примера:

```bash
cp .env.example .env
```

| Переменная     | Описание                     | Пример                              |
|----------------|------------------------------|-------------------------------------|
| DATABASE_URL   | подключение к PostgreSQL    | postgresql://postgres:postgres@db:5432/blog |
| REDIS_URL      | подключение к Redis          | redis://redis:6379/0                |
| CACHE_TTL      | время жизни кеша (сек)       | 300                                 |

## API эндпоинты

| Действие        | Метод | Эндпоинт      |
|-----------------|-------|---------------|
| Создать пост    | POST  | /posts        |
| Получить список | GET   | /posts        |
| Получить пост   | GET   | /posts/{id}   |
| Обновить пост   | PUT   | /posts/{id}   |
| Удалить пост    | DELETE| /posts/{id}   |

## Кеширование

Используется стратегия **cache-aside**.

**Алгоритм работы:**

1. При запросе `GET /posts/{id}` сервис сначала проверяет Redis
2. Если ключ найден → возвращается значение из кеша
3. Если нет → данные читаются из PostgreSQL
4. Результат сохраняется в Redis

**Ключ кеша:** `post:{id}`

Пример: `post:1`, `post:42`

**TTL**

Каждый ключ имеет время жизни.

- По умолчанию: **300 секунд**
- Настраивается через переменную: `CACHE_TTL`

### Инвалидация кеша

При изменении данных кеш очищается:

- `PUT /posts/{id}`
- `DELETE /posts/{id}`

Удаляется ключ: `DEL post:{id}`

Это гарантирует, что следующий запрос снова прочитает данные из базы.

## Тестирование

Интеграционный тест проверяет:

1. **Cache miss** — первый `GET /posts/{id}`: данные читаются из PostgreSQL и сохраняются в Redis.
2. **Cache hit** — второй `GET /posts/{id}`: ответ возвращается из Redis (без обращения к БД).
3. **Cache invalidation** — после PUT или DELETE ключ удаляется и следующий запрос снова читает из базы.

Запуск:

```bash
pytest -q
```

## Пример запроса

Создание поста:

```
POST /posts
{
  "title": "Hello",
  "content": "First post"
}
```

Ответ:

```json
{
  "id": 1,
  "title": "Hello",
  "content": "First post"
}
```

## Что демонстрирует проект

- проектирование REST API
- работу с PostgreSQL
- работу с Redis
- стратегию кеширования cache-aside
- инвалидацию кеша
- интеграционные тесты
- контейнеризацию backend-сервиса
