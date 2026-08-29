"""
Shared pytest fixtures.

Two client fixtures are provided:

- `api_client`      -> unauthenticated, for public endpoints (GET /users, etc.)
- `authenticated_client` -> logs in via POST /auth/login first, then attaches
                            the real JWT accessToken to every request

Base URL and test-user credentials are read from environment variables, so
the SAME test suite can point at a different API/user just by changing
env vars in CI — no code changes needed.
"""

import os
import sys
from pathlib import Path

# Make `utils/` importable when running pytest from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from dotenv import load_dotenv
from utils.api_client import APIClient

load_dotenv()


@pytest.fixture(scope="session")
def api_client():
    """Unauthenticated client — used for public/open endpoints."""
    base_url = os.getenv("API_BASE_URL", "https://dummyjson.com")
    return APIClient(base_url, headers={"Content-Type": "application/json"})


@pytest.fixture(scope="session")
def auth_token(api_client):
    """
    Logs in ONCE per test run and returns the JWT accessToken.

    Session-scoped on purpose: logging in is expensive (a real network
    call), and every test that needs auth can just reuse this same token
    instead of logging in again.
    """
    username = os.getenv("API_TEST_USERNAME", "emilys")
    password = os.getenv("API_TEST_PASSWORD", "emilyspass")

    response = api_client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 200, (
        f"Login failed with status {response.status_code}: {response.text}"
    )

    token = response.json().get("accessToken")
    assert token, "Login succeeded but no accessToken was returned"
    return token


@pytest.fixture(scope="session")
def authenticated_client(auth_token):
    """Client pre-loaded with a real Bearer token from the login fixture."""
    base_url = os.getenv("API_BASE_URL", "https://dummyjson.com")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    return APIClient(base_url, headers=headers)


@pytest.fixture
def latency_budget_ms():
    """SLA threshold reused by multiple tests — change it in one place."""
    return 800
