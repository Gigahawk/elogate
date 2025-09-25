from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELOGATE_")  # pyright: ignore [reportUnannotatedClassAttribute]

    htpasswd: Path = Path("htpasswd")
    db_path: Path = Path("database.sqlite3")
    resources_path: Path = Path("elogate_resources")
    bind_ip: str = "127.0.0.1"
    bind_port: int = 8080
    secret_path: Path = Path("secret")
