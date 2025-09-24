import pytest_asyncio
from tortoise import Tortoise

from elogate.database import TORTOISE_ORM


@pytest_asyncio.fixture(scope="function")
async def init_db():
    test_config = TORTOISE_ORM.copy()
    test_config["connections"] = {  # pyright: ignore [reportArgumentType]
        "default": "sqlite://:memory:"
    }

    await Tortoise.init(config=test_config)
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()
