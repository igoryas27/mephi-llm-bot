# Двухсервисная система LLM-консультаций

## Архитектура

Проект состоит из двух сервисов:

- **Auth Service** — регистрация, логин, выпуск JWT
- **Bot Service** — Telegram-бот, проверка JWT, постановка LLM-задач в очередь

### Компоненты
- FastAPI
- aiogram
- SQLAlchemy + SQLite
- Redis
- RabbitMQ
- Celery
- OpenRouter

## Сценарий работы

1. Пользователь регистрируется в Auth Service
2. Логинится и получает JWT
3. Отправляет JWT боту командой `/token <jwt>`
4. Бот сохраняет JWT в Redis
5. При обычном сообщении бот валидирует токен
6. Бот ставит задачу в RabbitMQ через Celery
7. Celery worker вызывает LLM через OpenRouter
8. Ответ отправляется пользователю в Telegram

## Запуск локально

### Auth Service
```bash
cd auth_service
uv sync
uv run python -m uvicorn app.main:app --reload --port 8000
```

### Скрины
1. регистрация
![](screenshots/s_auth)
2. логин
![](screenshots/s_login)
3. me
![](screenshots/s_me)
4. telegram
![](screenshots/s_telegram)
5. rabbitMQ
![](screenshots/s_rabbit)
6. Главная страница Swagger
![](screenshots/s_auth_service)
7. Tests
![](screenshots/s_tests)


