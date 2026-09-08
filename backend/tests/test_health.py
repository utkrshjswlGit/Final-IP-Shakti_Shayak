"""Tests for the /api/v1/health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    """Health endpoint must return HTTP 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_schema(client: AsyncClient) -> None:
    """Health endpoint must return the expected JSON structure."""
    response = await client.get("/api/v1/health")
    data = response.json()

    assert "status" in data
    assert "app_name" in data
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_health_app_name(client: AsyncClient) -> None:
    """Health endpoint app_name must match configuration."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "IP-SAKTI" in data["app_name"]


@pytest.mark.asyncio
async def test_health_environment_is_test(client: AsyncClient) -> None:
    """Health endpoint environment must reflect test environment."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["environment"] == "test"
