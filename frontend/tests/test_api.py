import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from frontend.api import backend_is_ready


@pytest.mark.parametrize(
    "status, payload, expected",
    [
        (200, {"status": "ok"}, True),
        (503, {"status": "unavailable"}, False),
        (200, {"status": "unknown"}, False),
    ],
)
def test_backend_readiness(status, payload, expected):
    response = httpx.Response(status, json=payload, request=httpx.Request("GET", "http://backend"))
    with patch("frontend.api.httpx.AsyncClient.get", new_callable=AsyncMock) as get:
        get.return_value = response
        assert asyncio.run(backend_is_ready()) is expected


def test_backend_connection_failure():
    with patch("frontend.api.httpx.AsyncClient.get", new_callable=AsyncMock) as get:
        get.side_effect = httpx.ConnectError("unreachable")
        assert asyncio.run(backend_is_ready()) is False
