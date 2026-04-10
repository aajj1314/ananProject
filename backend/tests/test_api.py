"""API integration tests for auth, device, and location flows."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


async def register_and_login(client, phone="13800138000", nickname="Guardian"):
    """Create a user and return an auth header."""

    register_payload = {
        "phone": phone,
        "password": "passw0rd",
        "nickname": nickname,
    }
    register_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"phone": register_payload["phone"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_auth_and_device_flow(client: AsyncClient):
    """Ensure user registration, login, and device binding work."""

    headers = await register_and_login(client)
    bind_response = await client.post(
        "/api/v1/device",
        json={"device_id": "123456789012345", "device_name": "Dad Insole"},
        headers=headers,
    )
    assert bind_response.status_code == 201
    assert bind_response.json()["data"]["device_name"] == "Dad Insole"

    list_response = await client.get("/api/v1/device", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["data"]) == 1

    update_response = await client.put(
        "/api/v1/device/123456789012345",
        json={"device_name": "Renamed Pair"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["device_name"] == "Renamed Pair"


@pytest.mark.asyncio
async def test_auth_error_scenarios(client: AsyncClient):
    """Test authentication error scenarios."""

    # Test invalid phone format
    bad_phone_response = await client.post(
        "/api/v1/auth/register",
        json={"phone": "123", "password": "passw0rd", "nickname": "Test"},
    )
    assert bad_phone_response.status_code == 422

    # Test login with non-existent user
    bad_login_response = await client.post(
        "/api/v1/auth/login",
        json={"phone": "13999999999", "password": "wrongpass"},
    )
    assert bad_login_response.status_code in (401, 404)

    # Test invalid token
    invalid_token_response = await client.get(
        "/api/v1/device",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert invalid_token_response.status_code == 401

    # Test missing token
    missing_token_response = await client.get("/api/v1/device")
    assert missing_token_response.status_code == 401


@pytest.mark.asyncio
async def test_user_profile_endpoint(client: AsyncClient):
    """Test the user profile endpoint."""

    headers = await register_and_login(client, phone="13800138001", nickname="ProfileTest")

    profile_response = await client.get("/api/v1/auth/profile", headers=headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()["data"]
    assert profile_data["nickname"] == "ProfileTest"
    assert profile_data["phone"] == "13800138001"
    assert profile_data["role"] in ["user", "admin"]


@pytest.mark.asyncio
async def test_device_access_control(client: AsyncClient):
    """Test that users can't access other users' devices."""

    # User 1 creates a device
    headers1 = await register_and_login(client, phone="13800138100", nickname="User1")
    await client.post(
        "/api/v1/device",
        json={"device_id": "999888777666555", "device_name": "User1 Device"},
        headers=headers1,
    )

    # User 2 tries to access User 1's device
    headers2 = await register_and_login(client, phone="13800138200", nickname="User2")
    get_response = await client.get(
        "/api/v1/device/999888777666555",
        headers=headers2,
    )
    # Should return 404 or 403, not 200
    assert get_response.status_code in (403, 404)

    # User 2 tries to update User 1's device
    update_response = await client.put(
        "/api/v1/device/999888777666555",
        json={"device_name": "Hacked!"},
        headers=headers2,
    )
    assert update_response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_admin_endpoints_denied_for_regular_users(client: AsyncClient):
    """Test that regular users can't access admin endpoints."""

    headers = await register_and_login(client, phone="13800138300", nickname="RegularUser")

    # Try to access admin stats
    admin_response = await client.get("/api/v1/admin/stats", headers=headers)
    assert admin_response.status_code == 403

    # Try to list all users
    users_response = await client.get("/api/v1/admin/users", headers=headers)
    assert users_response.status_code == 403


@pytest.mark.asyncio
async def test_health_checks(client: AsyncClient):
    """Test health check endpoints."""

    # Basic health
    health_response = await client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    # API health
    api_health_response = await client.get("/api/v1/health")
    assert api_health_response.status_code == 200

    # Detailed health (requires auth but is public in our implementation)
    detailed_response = await client.get("/api/v1/health/detailed")
    assert detailed_response.status_code == 200

    # Metrics
    metrics_response = await client.get("/api/v1/health/metrics")
    assert metrics_response.status_code == 200


async def test_location_ingest_and_history(client):
    """Ensure telemetry ingestion feeds latest and history queries."""

    headers = await register_and_login(client)
    await client.post(
        "/api/v1/device",
        json={"device_id": "123456789012345", "device_name": "Outdoor Pair"},
        headers=headers,
    )
    fence_response = await client.post(
        "/api/v1/fence/123456789012345",
        json={
            "name": "Home Zone",
            "center_latitude": 39.1028,
            "center_longitude": 117.3475,
            "radius_meters": 150,
            "is_active": True,
        },
        headers=headers,
    )
    assert fence_response.status_code == 201
    assert fence_response.json()["data"]["name"] == "Home Zone"

    now = datetime.now(timezone.utc).replace(microsecond=0)
    telemetry = {
        "device_id": "123456789012345",
        "timestamp": now.isoformat(),
        "latitude": 39.1028,
        "longitude": 117.3475,
        "altitude": 50.5,
        "alarm_type": 0,
        "battery": 15,
        "speed": 1.2,
        "direction": 90,
    }
    ingest_response = await client.post("/api/v1/location/ingest", json=telemetry)
    assert ingest_response.status_code == 201
    assert ingest_response.json()["data"]["alarm_type"] == 4
    assert ingest_response.json()["data"]["fence_events"][0]["status"] == "inside"

    latest_response = await client.get("/api/v1/location/123456789012345", headers=headers)
    assert latest_response.status_code == 200
    assert latest_response.json()["data"]["battery"] == 15

    history_response = await client.get(
        "/api/v1/location/history/123456789012345",
        params={
            "start_time": (now - timedelta(minutes=5)).isoformat(),
            "end_time": (now + timedelta(minutes=5)).isoformat(),
        },
        headers=headers,
    )
    assert history_response.status_code == 200
    assert len(history_response.json()["data"]) == 1

    summary_response = await client.get(
        "/api/v1/location/summary/123456789012345",
        params={
            "start_time": (now - timedelta(minutes=5)).isoformat(),
            "end_time": (now + timedelta(minutes=5)).isoformat(),
        },
        headers=headers,
    )
    assert summary_response.status_code == 200
    assert summary_response.json()["data"]["alarms_detected"] == 1

    alarm_response = await client.get("/api/v1/alarm/history/123456789012345", headers=headers)
    assert alarm_response.status_code == 200
    assert len(alarm_response.json()["data"]) == 1

    notification_response = await client.get(
        "/api/v1/alarm/notifications/123456789012345",
        headers=headers,
    )
    assert notification_response.status_code == 200
    assert len(notification_response.json()["data"]) == 1

    breach_response = await client.post(
        "/api/v1/location/ingest",
        json={
            "device_id": "123456789012345",
            "timestamp": (now + timedelta(minutes=10)).isoformat(),
            "latitude": 39.1128,
            "longitude": 117.3675,
            "altitude": 52.0,
            "alarm_type": 0,
            "battery": 70,
            "speed": 1.8,
            "direction": 130,
        },
    )
    assert breach_response.status_code == 201
    assert breach_response.json()["data"]["alarm_type"] == 6
    assert breach_response.json()["data"]["fence_events"][0]["status"] == "outside"
    assert breach_response.json()["data"]["fence_events"][0]["transitioned"] is True

    repeated_breach_response = await client.post(
        "/api/v1/location/ingest",
        json={
            "device_id": "123456789012345",
            "timestamp": (now + timedelta(minutes=11)).isoformat(),
            "latitude": 39.1135,
            "longitude": 117.368,
            "altitude": 52.5,
            "alarm_type": 0,
            "battery": 68,
            "speed": 1.5,
            "direction": 120,
        },
    )
    assert repeated_breach_response.status_code == 201
    assert repeated_breach_response.json()["data"]["alarm_type"] == 0
    assert repeated_breach_response.json()["data"]["fence_events"][0]["transitioned"] is False

    fence_list_response = await client.get("/api/v1/fence/123456789012345", headers=headers)
    assert fence_list_response.status_code == 200
    assert fence_list_response.json()["data"][0]["last_status"] == "outside"

    updated_fence_response = await client.put(
        f"/api/v1/fence/123456789012345/{fence_response.json()['data']['id']}",
        json={
            "name": "Expanded Home Zone",
            "center_latitude": 39.1028,
            "center_longitude": 117.3475,
            "radius_meters": 5000,
            "is_active": True,
        },
        headers=headers,
    )
    assert updated_fence_response.status_code == 200
    assert updated_fence_response.json()["data"]["name"] == "Expanded Home Zone"

    alarm_response = await client.get("/api/v1/alarm/history/123456789012345", headers=headers)
    assert alarm_response.status_code == 200
    assert len(alarm_response.json()["data"]) == 2
    assert alarm_response.json()["data"][0]["alarm_type"] == 6

    notification_response = await client.get(
        "/api/v1/alarm/notifications/123456789012345",
        headers=headers,
    )
    assert notification_response.status_code == 200
    assert len(notification_response.json()["data"]) == 2
    assert "电子围栏越界" in notification_response.json()["data"][0]["title"]

    delete_fence_response = await client.delete(
        f"/api/v1/fence/123456789012345/{fence_response.json()['data']['id']}",
        headers=headers,
    )
    assert delete_fence_response.status_code == 200

    delete_response = await client.delete("/api/v1/device/123456789012345", headers=headers)
    assert delete_response.status_code == 200
