"""Small UI helpers shared by the pages."""

from nicegui import ui

from frontend.api import ApiError


def show_error(exc: ApiError):
    ui.notify(str(exc), type="negative")
    if exc.status == 401:
        ui.navigate.to("/login")


async def call_api(coroutine, success=None):
    """Await an API call. Returns (ok, data) and shows a notification either way."""
    try:
        data = await coroutine
    except ApiError as exc:
        show_error(exc)
        return False, None
    if success:
        ui.notify(success, type="positive")
    return True, data


def section_title(text):
    return ui.label(text).classes("text-lg font-medium")


def kg(value):
    """Format a kg CO2e amount (str or number from the API)."""
    return f"{float(value or 0):,.2f} kg CO2e"
