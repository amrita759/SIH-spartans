import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    reg_payload = {
        "name": "Officer Sharma",
        "email": "sharma@i4c.gov.in",
        "password": "SecurePassword123!",
        "role": "I4C_OFFICER",
        "organization": "I4C Cyber Unit",
        "state": "Delhi",
        "district": "New Delhi"
    }

    response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "sharma@i4c.gov.in"

    # Login
    login_payload = {
        "username": "sharma@i4c.gov.in",
        "password": "SecurePassword123!"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data