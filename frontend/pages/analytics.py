from nicegui import ui

from frontend.layout import page_layout


@ui.page("/dashboard")
def page():
    with page_layout("Analytics Dashboard & Reporting"):
        ui.label("Emissions charts, filters, KPIs, and report exports will be built here.")
        ui.label("Not implemented yet.").classes("text-gray-500")
