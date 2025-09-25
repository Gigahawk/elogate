from elogate.config import Settings

TORTOISE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": Settings().sqlite_db_path},
        }
    },
    "apps": {
        "elogate": {
            "models": ["elogate.models", "aerich.models"],
            "default_connection": "default",
            # Always store time as UTC in database
            "use_tz": True,
        },
    },
}
