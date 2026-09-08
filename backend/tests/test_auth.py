"""Tests for authentication endpoints — register, login, /me."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_creates_user(client: AsyncClient) -> None:
    """POST /auth/register should create a user and return their profile."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client: AsyncClient) -> None:
    """Registering with an existing email should return 422."""
    payload = {"email": "duplicate@example.com", "password": "SecurePass123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_returns_token(client: AsyncClient) -> None:
    """POST /auth/login with valid credentials should return a JWT."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login_test@example.com", "password": "SecurePass123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client: AsyncClient) -> None:
    """Login with wrong password should return 401."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "password": "SecurePass123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_login_unknown_email_rejected(client: AsyncClient) -> None:
    """Login with non-existent email should return 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_profile(client: AsyncClient) -> None:
    """GET /auth/me with valid token should return user profile."""
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me_test@example.com", "password": "SecurePass123"},
    )
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "me_test@example.com", "password": "SecurePass123"},
    )
    token = login_response.json()["access_token"]

    # Get profile
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me_test@example.com"


@pytest.mark.asyncio
async def test_me_without_token_rejected(client: AsyncClient) -> None:
    """GET /auth/me without a token should return 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_short_password_rejected(client: AsyncClient) -> None:
    """Passwords shorter than 8 chars should fail validation."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert response.status_code == 422
