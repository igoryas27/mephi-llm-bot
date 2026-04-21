from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except ExpiredSignatureError as e:
        raise ValueError("Token expired") from e
    except JWTError as e:
        raise ValueError("Invalid token") from e

    if "sub" not in payload:
        raise ValueError("Token missing sub")

    return payload