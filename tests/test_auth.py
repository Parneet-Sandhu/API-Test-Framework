"""
Tests for the authentication flow against DummyJSON (https://dummyjson.com).

This demonstrates a REAL auth flow, not just public GET requests:
  1. POST /auth/login with credentials -> get back a real JWT accessToken
  2. Use that token as a Bearer token on protected endpoints
  3. Prove that a bad password is correctly rejected

Note: DummyJSON's "real" users/passwords are published in their own docs
for testing purposes only (e.g. username "emilys" / password "emilyspass").
This is expected and safe — it's a public sandbox API with no real data.
"""

import pytest
from utils.validators import validate_schema

LOGIN_SCHEMA = "schemas/auth_login_schema.json"


@pytest.mark.smoke
def test_login_success_returns_valid_token(api_client):
    response = api_client.post(
        "/auth/login",
        json={"username": "emilys", "password": "emilyspass"},
    )

    assert response.status_code == 200
    body = response.json()
    validate_schema(body, LOGIN_SCHEMA)

    # A JWT has 3 dot-separated parts: header.payload.signature
    assert body["accessToken"].count(".") == 2


@pytest.mark.regression
def test_login_with_wrong_password_is_rejected(api_client):
    response = api_client.post(
        "/auth/login",
        json={"username": "emilys", "password": "definitely-wrong-password"},
    )
    assert response.status_code in (400, 401)


@pytest.mark.regression
def test_login_with_missing_fields_is_rejected(api_client):
    response = api_client.post("/auth/login", json={"username": "emilys"})
    assert response.status_code in (400, 401, 422)


@pytest.mark.smoke
def test_authenticated_request_succeeds(authenticated_client):
    """Uses the `authenticated_client` fixture — meaning the login already
    happened in conftest.py and the token is already attached."""
    response = authenticated_client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "emilys"


@pytest.mark.regression
def test_protected_endpoint_rejects_missing_token(api_client):
    """Same endpoint as above, but with the UNauthenticated client —
    should be rejected since no token is attached."""
    response = api_client.get("/auth/me")
    assert response.status_code in (401, 403)
