import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as e:
        raise RuntimeError(f"OpenRouter request failed: {e}") from e

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter returned {response.status_code}: {response.text}"
        )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response: {data}") from e