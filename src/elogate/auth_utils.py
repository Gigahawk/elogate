from nicegui import ui, app

# TODO: real passwords
passwords = {"admin": "admin"}


def check_login(username: str, password: str) -> bool:
    # TODO: real login
    if passwords.get(username) == password:
        return True
    return False


def logout():
    dm_setting: bool | None = app.storage.user.get("dark_mode", None)  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
    app.storage.user.clear()
    app.storage.user["dark_mode"] = dm_setting
    ui.navigate.reload()


def logged_in() -> bool:
    authenticated: bool = app.storage.user.get("authenticated", False)  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
    if authenticated:
        return True
    return False
