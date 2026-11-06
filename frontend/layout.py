from contextlib import contextmanager

from nicegui import ui

from frontend import api, session


async def logout():
    try:
        await api.post("accounts/logout/")
    except api.ApiError:
        pass  # The local session is cleared either way.
    session.sign_out()
    ui.navigate.to("/login")


@contextmanager
def page_layout(title):
    with ui.header().classes("items-center bg-emerald-900"):
        ui.link("CarbonDesk", "/").classes("text-white text-xl font-bold no-underline")
        with ui.row().classes("gap-4"):
            for label, route in [
                ("Emissions", "/emissions"),
                ("Dashboard", "/dashboard"),
                ("Assistant", "/assistant"),
                ("Organisation", "/organisation"),
            ]:
                ui.link(label, route).classes("text-white")
        ui.space()
        user = session.user()
        if session.token() and user:
            organisation = (user.get("organisation") or {}).get("name", "")
            ui.label(f"{user['username']} · {organisation}").classes("text-white text-sm")
            ui.button("Log out", on_click=logout).props("flat color=white dense")
        else:
            ui.link("Log in", "/login").classes("text-white")
    with ui.column().classes("w-full max-w-5xl mx-auto p-6 gap-4"):
        ui.label(title).classes("text-3xl font-semibold")
        yield
