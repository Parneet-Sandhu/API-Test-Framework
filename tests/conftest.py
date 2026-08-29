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


DEFAULT_BASE_URL = "https://dummyjson.com"


def _get_base_url():
    """Reads API_BASE_URL, falling back to the default if it's
    missing OR set to an empty string (os.getenv's default arg only
    covers the missing case, not an empty-but-present env var).

    Also strips whitespace/newlines — a trailing newline in a GitHub
    secret (e.g. from a copy-paste) silently breaks DNS resolution
    with a cryptic 'Name or service not known' error otherwise.
    """
    value = os.getenv("API_BASE_URL", "").strip()
    return value or DEFAULT_BASE_URL


@pytest.fixture(scope="session")
def api_client():
    """Unauthenticated client — used for public/open endpoints."""
    return APIClient(_get_base_url(), headers={"Content-Type": "application/json"})


@pytest.fixture(scope="session")
def auth_token(api_client):
    """
    Logs in ONCE per test run and returns the JWT accessToken.

    Session-scoped on purpose: logging in is expensive (a real network
    call), and every test that needs auth can just reuse this same token
    instead of logging in again.
    """
    username = (os.getenv("API_TEST_USERNAME") or "emilys").strip()
    password = (os.getenv("API_TEST_PASSWORD") or "emilyspass").strip()

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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    return APIClient(_get_base_url(), headers=headers)


@pytest.fixture
def latency_budget_ms():
    """SLA threshold reused by multiple tests — change it in one place."""
    return 800
