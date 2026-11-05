from contextlib import contextmanager

from nicegui import ui


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
    with ui.column().classes("w-full max-w-5xl mx-auto p-6 gap-4"):
        ui.label(title).classes("text-3xl font-semibold")
        yield
