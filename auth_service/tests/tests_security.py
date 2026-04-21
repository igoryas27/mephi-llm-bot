from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hashing():
    password = "secret123"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong_password", password_hash) is False


def test_create_and_decode_token():
    token = create_access_token(sub="123", role="user")
    payload = decode_token(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload