"""Tests for the security module — JWT and password utilities."""

import pytest
from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import AuthenticationError


def test_hash_password_produces_different_hash_each_time() -> None:
    """bcrypt is salted — same password should produce different hashes."""
    h1 = hash_password("mysecretpassword")
    h2 = hash_password("mysecretpassword")
    assert h1 != h2


def test_verify_password_correct() -> None:
    """verify_password should return True for correct password."""
    hashed = hash_password("mysecretpassword")
    assert verify_password("mysecretpassword", hashed) is True


def test_verify_password_wrong() -> None:
    """verify_password should return False for wrong password."""
    hashed = hash_password("mysecretpassword")
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token() -> None:
    """A token created with create_access_token must be decodable."""
    token = create_access_token(subject="user-uuid-123")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-uuid-123"


def test_decode_invalid_token_raises() -> None:
    """decode_access_token should raise AuthenticationError for garbage tokens."""
    with pytest.raises(AuthenticationError):
        decode_access_token("this.is.not.a.valid.jwt")


def test_token_extra_claims() -> None:
    """Extra claims should appear in decoded payload."""
    token = create_access_token(subject="user-uuid-456", extra_claims={"role": "admin"})
    payload = decode_access_token(token)
    assert payload["role"] == "admin"
