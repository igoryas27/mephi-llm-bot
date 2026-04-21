from datetime import datetime, timedelta, timezone

from jose import jwt
import pytest

from app.bot import handlers
from app.core.config import settings


class DummyUser:
    def __init__(self, user_id: int):
        self.id = user_id


class DummyChat:
    def __init__(self, chat_id: int):
        self.id = chat_id


class DummyMessage:
    def __init__(self, text: str, user_id: int = 100):
        self.text = text
        self.from_user = DummyUser(user_id)
        self.chat = DummyChat(user_id)
        self.answers = []

    async def answer(self, text: str):
        self.answers.append(text)


def make_token():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "role": "user",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


@pytest.mark.asyncio
async def test_token_handler_saves_token(fake_redis, mocker):
    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)

    token = make_token()
    message = DummyMessage(f"/token {token}")

    await handlers.token_handler(message)

    saved = await fake_redis.get("token:100")
    assert saved == token
    assert message.answers[-1] == "Токен сохранен. Можно отправлять запросы модели."


@pytest.mark.asyncio
async def test_text_handler_without_token(fake_redis, mocker):
    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)

    message = DummyMessage("Привет")

    await handlers.text_handler(message)

    assert message.answers[-1] == "Нет JWT. Сначала авторизуйся через /token <jwt>."


@pytest.mark.asyncio
async def test_text_handler_with_token(fake_redis, mocker):
    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)
    delay_mock = mocker.patch("app.bot.handlers.llm_request.delay")

    token = make_token()
    await fake_redis.set("token:100", token)

    message = DummyMessage("Расскажи про градиентный бустинг")

    await handlers.text_handler(message)

    delay_mock.assert_called_once_with(message.chat.id, message.text)
    assert message.answers[-1] == "Запрос принят в обработку."