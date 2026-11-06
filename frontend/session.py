"""The logged-in user's token and profile, kept in NiceGUI's server-side user storage."""

from nicegui import app

EDIT_ROLES = {"admin", "editor"}


def _store():
    return app.storage.user


def token():
    return _store().get("token")


def user():
    return _store().get("user") or {}


def sign_in(payload):
    _store().update(token=payload["token"], user=payload["user"])


def sign_out():
    _store().pop("token", None)
    _store().pop("user", None)


def is_admin():
    return user().get("role") == "admin"


def can_edit():
    return user().get("role") in EDIT_ROLES
