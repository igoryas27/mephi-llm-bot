from aiogram import Bot

from app.core.config import settings


def get_bot() -> Bot:
    return Bot(token=settings.TELEGRAM_BOT_TOKEN)