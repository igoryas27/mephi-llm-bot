import httpx
import pytest
import respx

from app.services.openrouter_client import call_openrouter


@respx.mock
@pytest.mark.asyncio
async def test_call_openrouter_success():
    route = respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Это тестовый ответ от LLM"
                        }
                    }
                ]
            },
        )
    )

    result = await call_openrouter("Привет")

    assert route.called
    assert result == "Это тестовый ответ от LLM"