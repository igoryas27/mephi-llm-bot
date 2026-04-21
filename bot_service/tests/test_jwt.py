from datetime import datetime, timedelta, timezone

from jose import jwt
import pytest

from app.core.config import settings
from app.core.jwt import decode_and_validate


def test_decode_valid_token():
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "role": "user",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

    decoded = decode_and_validate(token)
    assert decoded["sub"] == "1"


def test_decode_invalid_token():
    with pytest.raises(ValueError):
        decode_and_validate("garbage.token.value")