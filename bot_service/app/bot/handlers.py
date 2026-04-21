from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request


router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Это бот с доступом к LLM по JWT - токену.\nСначала отправьте команду /token <JWT>")


@router.message(Command("token"))
async def token_handler(message: Message):
    parts = message.text.split(maxsplit=1) if message.text else []

    if len(parts) < 2:
        await message.answer("Использование: /token <jwt>")
        return

    token = parts[1].strip()

    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer("Токен невалиден или истёк.")
        return

    redis_client = get_redis()
    await redis_client.set(f"token:{message.from_user.id}", token)

    await message.answer("Токен сохранен. Можно отправлять запросы модели.")


@router.message()
async def text_handler(message: Message):
    redis_client = get_redis()
    token = await redis_client.get(f"token:{message.from_user.id}")

    if not token:
        await message.answer("Нет JWT. Сначала авторизуйся через /token <jwt>.")
        return

    try:
        decode_and_validate(token)
    except ValueError:
        await message.answer("JWT невалиден или истёк. Отправь новый через /token <jwt>.")
        return

    llm_request.delay(message.chat.id, message.text)
    await message.answer("Запрос принят в обработку.")