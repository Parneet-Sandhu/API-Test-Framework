"""
Reusable API client that wraps the `requests` library.

Why this exists:
- Avoids repeating base URL / headers / timing logic in every test
- Every response gets `.elapsed_ms` attached automatically, so any test
  can assert on latency without extra code
"""

import time
import requests


class APIClient:
    def __init__(self, base_url: str, headers: dict | None = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        response.elapsed_ms = (time.time() - start) * 1000
        return response

    def get(self, endpoint: str, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs):
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)
