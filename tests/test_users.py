"""
Tests for the /users endpoint on DummyJSON.

Each test checks one of the three things the framework promises:
- correctness (status code, data returned)
- schema compliance (shape of the JSON)
- latency (response time under budget)

These use the PUBLIC `api_client` fixture — no login needed for
reading user data (auth is only demonstrated in test_auth.py, where
it actually matters — e.g. /auth/me).
"""

import pytest
from utils.validators import validate_schema

SCHEMA_PATH = "schemas/dummyjson_user_schema.json"


@pytest.mark.smoke
def test_get_single_user_status_code(api_client):
    response = api_client.get("/users/1")
    assert response.status_code == 200


@pytest.mark.smoke
def test_get_single_user_schema(api_client):
    response = api_client.get("/users/1")
    validate_schema(response.json(), SCHEMA_PATH)


@pytest.mark.regression
def test_get_single_user_latency(api_client, latency_budget_ms):
    response = api_client.get("/users/1")
    assert response.elapsed_ms < latency_budget_ms, (
        f"Response took {response.elapsed_ms:.0f}ms, "
        f"budget is {latency_budget_ms}ms"
    )


@pytest.mark.regression
@pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
def test_multiple_users_return_valid_schema(api_client, user_id):
    """Same test logic reused across many inputs — this is what lets
    a framework like this scale across microservices without
    duplicating code."""
    response = api_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    validate_schema(response.json(), SCHEMA_PATH)


@pytest.mark.regression
def test_get_nonexistent_user_returns_404(api_client):
    response = api_client.get("/users/999999")
    assert response.status_code == 404


@pytest.mark.regression
def test_get_all_users_returns_list(api_client):
    response = api_client.get("/users")
    assert response.status_code == 200
    body = response.json()
    assert "users" in body
    assert isinstance(body["users"], list)
    assert len(body["users"]) > 0
    for user in body["users"]:
        validate_schema(user, SCHEMA_PATH)
