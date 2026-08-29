"""
Tests for the /posts endpoint on DummyJSON.

Covers a public GET, a simulated POST (create), and one example of
using the AUTHENTICATED client for a write — showing the token from
conftest.py's login fixture actually being put to use.
"""

import pytest
from utils.validators import validate_schema

SCHEMA_PATH = "schemas/post_schema.json"


@pytest.mark.smoke
def test_get_single_post(api_client):
    response = api_client.get("/posts/1")
    assert response.status_code == 200
    validate_schema(response.json(), SCHEMA_PATH)


@pytest.mark.regression
def test_get_all_posts_returns_list(api_client):
    response = api_client.get("/posts")
    assert response.status_code == 200
    body = response.json()
    assert "posts" in body
    assert len(body["posts"]) > 0


@pytest.mark.regression
def test_create_post_unauthenticated(api_client):
    """DummyJSON's /posts/add doesn't require auth — but many real
    APIs would. This test documents the unauthenticated path."""
    payload = {
        "title": "API Test Automation",
        "body": "Validating POST requests work as expected",
        "userId": 1,
    }
    response = api_client.post("/posts/add", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["userId"] == payload["userId"]


@pytest.mark.smoke
def test_create_post_authenticated(authenticated_client):
    """Same create action, but sent through the authenticated_client —
    proving the login token from conftest.py flows all the way through
    to a real, authorized write request."""
    payload = {
        "title": "Created with an authenticated request",
        "body": "This request carried a real Bearer token",
        "userId": 1,
    }
    response = authenticated_client.post("/posts/add", json=payload)
    assert response.status_code == 201


@pytest.mark.regression
def test_get_posts_by_user(api_client):
    response = api_client.get("/posts/user/1")
    assert response.status_code == 200
    posts = response.json()["posts"]
    assert all(post["userId"] == 1 for post in posts)
