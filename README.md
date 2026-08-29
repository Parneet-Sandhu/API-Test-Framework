# API Test Automation Framework

A reusable REST API testing framework in Python (PyTest + Requests) that validates
endpoint correctness, JSON Schema compliance, status codes, response latency,
**and a real authentication flow** — wired into GitHub Actions so it runs
automatically on every pull request.

Tests run against the free public API [dummyjson.com](https://dummyjson.com),
which has a genuine login endpoint returning a real JWT — so this framework
demonstrates testing protected/authenticated endpoints, not just open GETs.

## Project structure

```
api-test-framework/
├── tests/
│   ├── conftest.py             # fixtures: api_client, auth_token, authenticated_client
│   ├── test_auth.py            # login flow: success, failure, token reuse
│   ├── test_users.py           # status code / schema / latency tests
│   └── test_posts.py           # public GET + authenticated POST examples
├── schemas/
│   ├── auth_login_schema.json
│   ├── dummyjson_user_schema.json
│   └── post_schema.json
├── utils/
│   ├── api_client.py           # thin wrapper around requests
│   └── validators.py           # JSON Schema validation helper
├── .github/workflows/
│   └── api-tests.yml           # CI pipeline
├── requirements.txt
├── pytest.ini
└── .env.example
```

## How the auth flow works

1. `test_auth.py::test_login_success_returns_valid_token` sends
   `POST /auth/login` with a username/password and checks it gets back
   a real JWT `accessToken`.
2. `conftest.py` has a session-scoped `auth_token` fixture that does this
   login **once** for the whole test run, and an `authenticated_client`
   fixture that attaches the token as `Authorization: Bearer <token>` to
   every request it makes.
3. Any test that needs to hit a protected endpoint just asks for the
   `authenticated_client` fixture as an argument — pytest handles the
   login and token attachment automatically, no extra code needed:

   ```python
   def test_authenticated_request_succeeds(authenticated_client):
       response = authenticated_client.get("/auth/me")
       assert response.status_code == 200
   ```

4. `test_protected_endpoint_rejects_missing_token` proves the negative
   case too — hitting the same endpoint with the plain `api_client`
   (no token) correctly gets rejected.

## Setup

```bash
git clone <your-repo-url>
cd api-test-framework
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # optional — defaults already point at the demo API
```

`.env` holds `API_BASE_URL`, `API_TEST_USERNAME`, and `API_TEST_PASSWORD`.
Defaults already work out of the box using DummyJSON's own published test
account, so you don't have to set anything to get started.

## Running the tests

```bash
# everything
pytest

# just the fast smoke checks
pytest -m smoke

# the full regression suite
pytest -m regression

# parallel, if you install pytest-xdist
pytest -n auto

# generates report.html automatically (see pytest.ini)
```

## Pointing it at a different API

Change the environment variables — no code changes needed:

```bash
export API_BASE_URL="https://your-staging-api.com"
export API_TEST_USERNAME="your-test-account-username"
export API_TEST_PASSWORD="your-test-account-password"
pytest
```

As long as your real API also has a `POST /auth/login`-style endpoint that
returns a token in the response body, you only need to change the field
name it's read from in `conftest.py`'s `auth_token` fixture
(currently `response.json().get("accessToken")`).

## How the CI pipeline works

On every pull request into `main`, `.github/workflows/api-tests.yml`:
1. Spins up Ubuntu + Python 3.11
2. Installs dependencies
3. Runs the smoke tests, then the full regression suite
4. Uploads an HTML report as a build artifact
5. Shows pass/fail directly on the PR

To use this on your own API, add `API_BASE_URL`, `API_TEST_USERNAME`, and
`API_TEST_PASSWORD` as **repo secrets** (Settings → Secrets and variables
→ Actions) — use a dedicated **test account**, never a real personal
account or production credentials.

## Extending it

- **New endpoint** → add a schema in `schemas/`, add a test file in `tests/`
  following the pattern in `test_users.py`
- **New assertion type** → add a helper in `utils/`
- **Different latency SLA per endpoint** → override the `latency_budget_ms`
  fixture in that specific test

## Why this design

- **`api_client` fixture is session-scoped** — one client, reused across all
  tests, so headers/auth are set up once, not per test
- **Schemas are separate JSON files**, not inline dicts — non-engineers
  (or an API contract doc) can review/update them without touching test code
- **`@pytest.mark.parametrize`** lets one test function cover many
  endpoints/inputs, which is what lets this scale "across microservices"
  without duplicating code
- **Markers (`smoke` / `regression`)** let CI run a fast subset on every
  push and the full suite on PRs, keeping feedback loops short
