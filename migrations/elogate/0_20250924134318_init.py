from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "game" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(256) NOT NULL UNIQUE,
    "ranking_model" VARCHAR(256) NOT NULL DEFAULT 'PlackettLuce',
    "ranking_model_args" JSON NOT NULL,
    "parent_id" INT REFERENCES "game" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "match" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "timestamp" TIMESTAMP NOT NULL UNIQUE DEFAULT CURRENT_TIMESTAMP,
    "modified" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "participants" JSON NOT NULL,
    "game_id" INT NOT NULL REFERENCES "game" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "player" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(256) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "playerrank" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "rank_idx" INT NOT NULL,
    "mu" REAL NOT NULL,
    "sigma" REAL NOT NULL,
    "game_id" INT NOT NULL REFERENCES "game" ("id") ON DELETE CASCADE,
    "match_id" INT NOT NULL REFERENCES "match" ("id") ON DELETE CASCADE,
    "player_id" INT NOT NULL REFERENCES "player" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
