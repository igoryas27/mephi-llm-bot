import asyncio

from app.bot.client import get_bot
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter


@celery_app.task(name="app.tasks.llm_tasks.llm_request")
def llm_request(tg_chat_id: int, prompt: str) -> str:
    return asyncio.run(_llm_request_impl(tg_chat_id, prompt))


async def _llm_request_impl(tg_chat_id: int, prompt: str) -> str:
    try:
        answer = await call_openrouter(prompt)
    except Exception as e:
        answer = f"Ошибка при обращении к LLM: {e}"

    bot = get_bot()
    try:
        await bot.send_message(chat_id=tg_chat_id, text=answer)
    finally:
        await bot.session.close()

    return answer