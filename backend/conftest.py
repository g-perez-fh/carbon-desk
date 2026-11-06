from decimal import Decimal

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from accounts.models import Organisation, User


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()


@pytest.fixture(autouse=True)
def no_openai_key(settings):
    """Tests never call the real AI service unless they opt in by mocking it."""
    settings.OPENAI_API_KEY = ""


@pytest.fixture
def organisation(db):
    return Organisation.objects.create(name="Acme GmbH", industry="Manufacturing")


@pytest.fixture
def make_member(organisation):
    def make(username, role=User.Role.VIEWER, org=None):
        return User.objects.create_user(
            username=username,
            password="a-test-password-only",
            organisation=org or organisation,
            role=role,
        )

    return make


@pytest.fixture
def admin_user(make_member):
    return make_member("alice", User.Role.ADMIN)


@pytest.fixture
def viewer_user(make_member):
    return make_member("victor", User.Role.VIEWER)


@pytest.fixture
def api_for():
    def client_for(user):
        client = APIClient()
        client.force_authenticate(user)
        return client

    return client_for


@pytest.fixture
def emissions(monkeypatch):
    """Stand in for the emissions subsystem: set kg CO2e per scope for any period."""
    values = {1: Decimal("0"), 2: Decimal("0"), 3: Decimal("0")}

    def totals_by_scope(organisation, start, end):
        return dict(values)

    monkeypatch.setattr("emissions.services.totals_by_scope", totals_by_scope, raising=False)
    return values
