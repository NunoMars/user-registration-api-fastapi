from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.conftest import InMemoryEmailClient


def register_user(
    client: TestClient,
    email_client: InMemoryEmailClient,
    email: str,
    password: str = "Secret123!",
) -> str:
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    return email_client.activation_codes[email.lower()]


def test_activate_user_with_valid_basic_auth_and_code(
    client: TestClient,
    email_client: InMemoryEmailClient,
) -> None:
    email = "activation@example.com"
    password = "Secret123!"
    code = register_user(client, email_client, email, password)

    response = client.post(
        "/api/v1/users/activate",
        json={"code": code},
        auth=(email, password),
    )

    assert response.status_code == 200

    body = response.json()
    assert body["email"] == email
    assert body["is_active"] is True


def test_activate_user_rejects_wrong_password(
    client: TestClient,
    email_client: InMemoryEmailClient,
) -> None:
    email = "wrong-password@example.com"
    code = register_user(client, email_client, email)

    response = client.post(
        "/api/v1/users/activate",
        json={"code": code},
        auth=(email, "WrongPassword123!"),
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_activate_user_rejects_wrong_code(
    client: TestClient,
    email_client: InMemoryEmailClient,
) -> None:
    email = "wrong-code@example.com"
    password = "Secret123!"
    register_user(client, email_client, email, password)

    response = client.post(
        "/api/v1/users/activate",
        json={"code": "9999"},
        auth=(email, password),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_OR_EXPIRED_ACTIVATION_CODE"


def test_activate_user_rejects_expired_code(
    client: TestClient,
    email_client: InMemoryEmailClient,
    db_execute: Callable[..., None],
) -> None:
    email = "expired-code@example.com"
    password = "Secret123!"
    code = register_user(client, email_client, email, password)

    db_execute(
        """
        UPDATE activation_codes
        SET expires_at = now() - interval '1 second'
        WHERE user_id = (
            SELECT id
            FROM users
            WHERE email = $1
        )
        """,
        email,
    )

    response = client.post(
        "/api/v1/users/activate",
        json={"code": code},
        auth=(email, password),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_OR_EXPIRED_ACTIVATION_CODE"


def test_activate_user_rejects_already_active_user(
    client: TestClient,
    email_client: InMemoryEmailClient,
) -> None:
    email = "already-active@example.com"
    password = "Secret123!"
    code = register_user(client, email_client, email, password)

    first_response = client.post(
        "/api/v1/users/activate",
        json={"code": code},
        auth=(email, password),
    )
    second_response = client.post(
        "/api/v1/users/activate",
        json={"code": code},
        auth=(email, password),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "USER_ALREADY_ACTIVE"


def test_activate_user_limits_wrong_code_attempts(
    client: TestClient,
    email_client: InMemoryEmailClient,
) -> None:
    email = "too-many-attempts@example.com"
    password = "Secret123!"
    register_user(client, email_client, email, password)

    for _ in range(4):
        response = client.post(
            "/api/v1/users/activate",
            json={"code": "9999"},
            auth=(email, password),
        )
        assert response.status_code == 400

    response = client.post(
        "/api/v1/users/activate",
        json={"code": "9999"},
        auth=(email, password),
    )

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "TOO_MANY_ACTIVATION_ATTEMPTS"
