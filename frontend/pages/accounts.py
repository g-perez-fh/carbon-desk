from nicegui import ui

from frontend.layout import page_layout


@ui.page("/organisation")
def page():
    with page_layout("Users, Organisation & Targets"):
        ui.label("User access, company structure, and reduction targets will be built here.")
        ui.label("Not implemented yet.").classes("text-gray-500")
