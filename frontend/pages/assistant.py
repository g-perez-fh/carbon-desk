from nicegui import ui

from frontend.layout import page_layout


@ui.page("/assistant")
def page():
    with page_layout("AI Sustainability Assistant"):
        ui.label("Company-data chat and reduction suggestions will be built here.")
        ui.label("Not implemented yet.").classes("text-gray-500")
