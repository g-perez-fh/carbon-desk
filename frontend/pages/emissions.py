from nicegui import ui

from frontend.layout import page_layout


@ui.page("/emissions")
def page():
    with page_layout("Emissions Data & Calculation"):
        ui.label("Activity forms, CSV imports, and emission calculations will be built here.")
        ui.label("Not implemented yet.").classes("text-gray-500")
