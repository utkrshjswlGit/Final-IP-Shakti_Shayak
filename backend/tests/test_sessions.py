"""Tests for sessions and assessment init endpoints."""

import pytest
from httpx import AsyncClient


async def _get_auth_header(client: AsyncClient, email: str, password: str = "SecurePass123") -> dict:
    """Helper: register + login and return auth header."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_session(client: AsyncClient) -> None:
    """POST /sessions should create a new workspace session."""
    headers = await _get_auth_header(client, "session_test1@example.com")
    response = await client.post(
        "/api/v1/sessions",
        json={"title": "Ashwagandha Formulation Analysis", "jurisdiction": "india"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Ashwagandha Formulation Analysis"
    assert data["current_jurisdiction"] == "india"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_sessions_returns_user_sessions_only(client: AsyncClient) -> None:
    """GET /sessions should only return sessions for the current user."""
    headers1 = await _get_auth_header(client, "list_test1@example.com")
    headers2 = await _get_auth_header(client, "list_test2@example.com")

    await client.post("/api/v1/sessions", json={"title": "User1 Session"}, headers=headers1)
    await client.post("/api/v1/sessions", json={"title": "User2 Session"}, headers=headers2)

    response = await client.get("/api/v1/sessions", headers=headers1)
    assert response.status_code == 200
    sessions = response.json()
    assert all(s["title"] != "User2 Session" for s in sessions)


@pytest.mark.asyncio
async def test_get_session_not_found(client: AsyncClient) -> None:
    """GET /sessions/{id} with a nonexistent ID should return 404."""
    headers = await _get_auth_header(client, "notfound_test@example.com")
    response = await client.get(
        "/api/v1/sessions/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_init_assessment(client: AsyncClient) -> None:
    """POST /sessions/{id}/assessments should create an assessment in INTAKE status."""
    headers = await _get_auth_header(client, "assessment_test@example.com")
    session_resp = await client.post("/api/v1/sessions", json={"jurisdiction": "india"}, headers=headers)
    session_id = session_resp.json()["id"]

    response = await client.post(
        f"/api/v1/sessions/{session_id}/assessments",
        json={"innovation_description": "An Ashwagandha-based Ayurvedic formulation for sleep support."},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "intake"
    assert "Ashwagandha" in data["innovation_description"]


@pytest.mark.asyncio
async def test_init_assessment_too_short_description(client: AsyncClient) -> None:
    """A description shorter than 20 chars should be rejected."""
    headers = await _get_auth_header(client, "short_desc@example.com")
    session_resp = await client.post("/api/v1/sessions", json={"jurisdiction": "india"}, headers=headers)
    session_id = session_resp.json()["id"]

    response = await client.post(
        f"/api/v1/sessions/{session_id}/assessments",
        json={"innovation_description": "Too short"},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sessions_require_auth(client: AsyncClient) -> None:
    """Session endpoints must reject unauthenticated requests."""
    response = await client.get("/api/v1/sessions")
    assert response.status_code == 401
