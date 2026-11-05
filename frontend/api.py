"""Server-side calls to Django. No database access belongs in the frontend."""

import os

import httpx


async def backend_is_ready():
    url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/api/health/")
            response.raise_for_status()
            return response.json().get("status") == "ok"
    except (httpx.HTTPError, ValueError, AttributeError):
        return False
