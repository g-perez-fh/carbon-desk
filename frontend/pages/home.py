from nicegui import ui

from frontend.api import backend_is_ready
from frontend.layout import page_layout


@ui.page("/")
def home():
    with page_layout("Company emissions, in one place"):
        ui.label("Track activity, understand emissions, and plan reductions.")
        ui.label("Project scaffold: the subsystem pages are ready for development.")
        status = ui.label("Backend connection has not been checked.")

        async def check_backend():
            ready = await backend_is_ready()
            status.set_text("Backend connected" if ready else "Backend unavailable")

        ui.button("Check backend connection", on_click=check_backend)
        ui.timer(0.1, check_backend, once=True)
