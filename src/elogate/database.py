TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": "default.sqlite3"},
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
