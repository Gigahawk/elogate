import traceback
from typing import override

from tortoise import Tortoise
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from nicegui import ui, app

from elogate.ui.pages.main_page import main_page  # pyright: ignore [reportUnusedImport]
from elogate.ui.pages.login_page import login_page  # pyright: ignore [reportUnusedImport]
from elogate.ui.pages.user_create_page import user_create_page  # pyright: ignore [reportUnusedImport]
from elogate.database import TORTOISE_CONFIG
from elogate.config import Settings

unrestricted_page_routes = {
    "/",
    "/login",
}


async def init_db() -> None:
    print("INIT DB")
    await Tortoise.init(config=TORTOISE_CONFIG)


async def close_db() -> None:
    await Tortoise.close_connections()


app.on_startup(init_db)  # pyright: ignore [reportUnknownMemberType]
app.on_shutdown(close_db)  # pyright: ignore [reportUnknownMemberType]


def app_exception(_ex: Exception):
    """
    We want to handle all REST API exceptions consistently across all pages in the app.
    """
    tb_txt = traceback.format_exc()

    def _clipboard_write():
        ui.clipboard.write(text=tb_txt)
        ui.notify(message="Copied to clipboard")

    with (
        ui.dialog() as dialog,
        ui.card().classes("w-full h-full").style("max-width: none"),
    ):
        _ = dialog.classes("w-full")
        with ui.row().classes("w-full"):
            _ = ui.label("Server Exception")
            _ = ui.space()
            _ = ui.button("Copy log", on_click=_clipboard_write)
            _ = ui.button(icon="close", on_click=dialog.close)
        log_view = ui.log().classes("w-full h-full")
        log_view.push(tb_txt)
        dialog.open()


app.on_exception(app_exception)  # pyright: ignore[reportUnknownMemberType]


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


def main(reload: bool = False):
    settings = Settings()
    with open(settings.secret_path, "r", encoding="utf-8") as f:
        ui.run(
            title="Elogate",
            storage_secret=f.read().strip(),
            host=settings.bind_ip,
            port=settings.bind_port,
            # reload MUST be set to False when running through project.scripts for some reason
            reload=reload,
        )


if __name__ in {"__main__", "__mp_main__"}:
    main(reload=True)
