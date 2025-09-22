from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "match" ADD "game_id" INT NOT NULL;
        CREATE TABLE IF NOT EXISTS "playerrank" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "rank_idx" INT NOT NULL,
    "mu" REAL NOT NULL,
    "sigma" REAL NOT NULL,
    "match_id" INT NOT NULL REFERENCES "match" ("id") ON DELETE CASCADE,
    "player_id" INT NOT NULL REFERENCES "player" ("id") ON DELETE CASCADE
);
        ALTER TABLE "match" ADD CONSTRAINT "fk_match_game_38a94396" FOREIGN KEY ("game_id") REFERENCES "game" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "match" DROP FOREIGN KEY "fk_match_game_38a94396";
        ALTER TABLE "match" DROP COLUMN "game_id";
        DROP TABLE IF EXISTS "playerrank";"""
