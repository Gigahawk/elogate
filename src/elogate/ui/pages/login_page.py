from fastapi.responses import RedirectResponse
from nicegui import ui, app

from elogate.auth_utils import check_login


@ui.page("/login")
async def login_page(redirect_to: str = "/") -> RedirectResponse | None:
    def try_login() -> None:
        uname: str = username.value  # pyright: ignore [reportAny]
        pword: str = password.value  # pyright: ignore [reportAny]
        if check_login(uname, pword):
            app.storage.user.update(
                {
                    "username": uname,
                    "authenticated": True,
                }
            )
            ui.navigate.to(redirect_to)
        else:
            ui.notify("Wrong username or password", color="negative")

    if app.storage.user.get("authenticated", False):  # pyright: ignore [reportUnknownMemberType]
        return RedirectResponse("/")

    with ui.card().classes("absolute-center"):
        username = ui.input("Username").on("keydown.enter", try_login)
        password = ui.input("Password", password=True, password_toggle_button=True).on(
            "keydown.enter", try_login
        )
        _ = ui.button("Log in", on_click=try_login)
