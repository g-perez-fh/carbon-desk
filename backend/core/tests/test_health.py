from unittest.mock import patch

import pytest
from django.db import DatabaseError


@pytest.mark.django_db
def test_health_checks_database(client):
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "carbondesk-backend"}


def test_health_returns_503_without_database_details(client):
    with patch("core.views.connection.cursor", side_effect=DatabaseError("private detail")):
        response = client.get("/api/health/")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


def test_health_rejects_writes(client):
    assert client.post("/api/health/").status_code == 405
