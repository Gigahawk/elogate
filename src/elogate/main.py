from typing import override

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from nicegui import ui, app

# TODO: real passwords
passwords = {"admin": "admin"    }
unrestricted_page_routes = {"/login"}


class AuthMiddleware(BaseHTTPMiddleware):
    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if not app.storage.user.get("authenticated", False):  # pyright: ignore [reportUnknownMemberType]
            if (
                not request.url.path.startswith("/_nicegui")
                and request.url.path not in unrestricted_page_routes
            ):
                return RedirectResponse(f"/login?redirect_to={request.url.path}")
        return await call_next(request)


app.add_middleware(AuthMiddleware)


@ui.page("/")
def main_page():
    def logout():
        app.storage.user.clear()
        ui.navigate.to("/login")

    with ui.column().classes("absolute-center items-center"):
        _ = ui.label(f"Hello {app.storage.user['username']}!").classes("text-2xl")
        _ = ui.button(on_click=logout, icon="logout").props("outline round")


@ui.page("/subpage")
def test_page():
    _ = ui.label("subpage")


@ui.page("/login")
def login(redirect_to: str = "/") -> RedirectResponse | None:
    def try_login() -> None:
        uname: str = username.value  # pyright: ignore [reportAny]
        pword: str = password.value  # pyright: ignore [reportAny]
        if passwords.get(uname) == pword:
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


def main(reload: bool = False):
    # reload MUST be set to False when running through project.scripts for some reason
    ui.run(title="Elogate", storage_secret="TODO_CHANGE_THIS", reload=reload)


if __name__ in {"__main__", "__mp_main__"}:
    main(reload=True)
