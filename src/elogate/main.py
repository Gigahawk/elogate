from typing import override

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from nicegui import ui, app

from elogate.ui.pages.main_page import main_page  # pyright: ignore [reportUnusedImport]
from elogate.ui.pages.login_page import login_page  # pyright: ignore [reportUnusedImport]
from elogate.ui.pages.user_create_page import user_create_page  # pyright: ignore [reportUnusedImport]
from elogate.config import Settings

unrestricted_page_routes = {
    "/",
    "/login",
}


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
