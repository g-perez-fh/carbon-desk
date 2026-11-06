from fastapi.responses import RedirectResponse
from nicegui import ui

from frontend import api, session
from frontend.components import call_api
from frontend.layout import page_layout


@ui.page("/login")
def login_page():
    if session.token():
        return RedirectResponse("/organisation")
    with page_layout("Log in"):
        with ui.card().classes("w-full max-w-md"):
            username = ui.input("Username").props("autofocus").classes("w-full")
            password = ui.input("Password", password=True, password_toggle_button=True)
            password.classes("w-full")

            async def submit():
                ok, payload = await call_api(
                    api.post(
                        "accounts/login/",
                        json={"username": username.value, "password": password.value},
                        auth=False,
                    )
                )
                if ok:
                    session.sign_in(payload)
                    ui.navigate.to("/organisation")

            password.on("keydown.enter", submit)
            ui.button("Log in", on_click=submit).classes("w-full")
            ui.link("New company? Create an account", "/register")


@ui.page("/register")
def register_page():
    if session.token():
        return RedirectResponse("/organisation")
    with page_layout("Register your company"):
        with ui.card().classes("w-full max-w-md"):
            ui.label("You become the administrator of your organisation.").classes("text-gray-600")
            fields = {
                "organisation_name": ui.input("Company name"),
                "industry": ui.input("Industry (optional)"),
                "country": ui.input("Country (optional)"),
                "username": ui.input("Username"),
                "email": ui.input("Email (optional)"),
                "password": ui.input("Password", password=True, password_toggle_button=True),
            }
            confirm = ui.input("Confirm password", password=True)
            for field in [*fields.values(), confirm]:
                field.classes("w-full")

            async def submit():
                if fields["password"].value != confirm.value:
                    ui.notify("The passwords do not match.", type="warning")
                    return
                payload = {name: field.value.strip() for name, field in fields.items()}
                payload["password"] = fields["password"].value
                ok, result = await call_api(
                    api.post("accounts/register/", json=payload, auth=False),
                    success="Welcome to CarbonDesk!",
                )
                if ok:
                    session.sign_in(result)
                    ui.navigate.to("/organisation")

            ui.button("Create account", on_click=submit).classes("w-full")
            ui.link("Already registered? Log in", "/login")
