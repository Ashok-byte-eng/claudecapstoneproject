import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_valid_params_returns_200(client: AsyncClient):
    response = await client.get(
        "/api/accommodations",
        params={"destination": "Lisbon", "check_in": "2026-08-01", "check_out": "2026-08-05", "guests": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "accommodations" in data


@pytest.mark.anyio
async def test_missing_destination_returns_422(client: AsyncClient):
    response = await client.get(
        "/api/accommodations",
        params={"check_in": "2026-08-01", "check_out": "2026-08-05", "guests": 2},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_invalid_guests_returns_422(client: AsyncClient):
    response = await client.get(
        "/api/accommodations",
        params={"destination": "Lisbon", "check_in": "2026-08-01", "check_out": "2026-08-05", "guests": 0},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_checkout_before_checkin_returns_422(client: AsyncClient):
    response = await client.get(
        "/api/accommodations",
        params={"destination": "Lisbon", "check_in": "2026-08-05", "check_out": "2026-08-01", "guests": 2},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_same_checkin_checkout_returns_422(client: AsyncClient):
    response = await client.get(
        "/api/accommodations",
        params={"destination": "Lisbon", "check_in": "2026-08-01", "check_out": "2026-08-01", "guests": 2},
    )
    assert response.status_code == 422
