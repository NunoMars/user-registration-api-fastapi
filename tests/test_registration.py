from fastapi.testclient import TestClient

from tests.conftest import InMemoryEmailClient


def test_register_user_creates_inactive_user_and_sends_code(
    client: TestClient,
    email_client: InMemoryEmailClient,
) -> None:
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "User@Test.com",
            "password": "Secret123!",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["email"] == "user@test.com"
    assert body["is_active"] is False
    assert "id" in body

    activation_code = email_client.activation_codes["user@test.com"]
    assert len(activation_code) == 4
    assert activation_code.isdigit()


def test_register_user_returns_conflict_when_email_already_exists(
    client: TestClient,
) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "Secret123!",
    }

    first_response = client.post("/api/v1/users/register", json=payload)
    second_response = client.post("/api/v1/users/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "error": {
            "code": "USER_ALREADY_EXISTS",
            "message": "A user with this email already exists.",
        }
    }


def test_register_user_rejects_weak_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "weak-password@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 422
