from datetime import datetime

import pytest
import pytest_asyncio
from tortoise import Tortoise

from elogate.database import TORTOISE_ORM
from elogate.models import RankingModels, Game, Player
from elogate.operations import create_match


@pytest_asyncio.fixture(scope="function")
async def init_db():
    test_config = TORTOISE_ORM.copy()
    test_config["connections"] = {"default": "sqlite://:memory:"}

    await Tortoise.init(config=test_config)
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_db(init_db):
    pool_game = Game(name="Pool")
    await pool_game.save()

    nine_ball = Game(name="9 Ball", parent=pool_game)
    await nine_ball.save()

    eight_ball = Game(name="8 Ball", parent=pool_game)
    await eight_ball.save()

    players = {}
    for name in ["Alice", "Bob", "Charlie", "Dan"]:
        players[name] = Player(name=name)
        await players[name].save()

    # Match 1: Alice beats Bob in 9 ball
    ts1 = datetime.fromtimestamp(30000)
    await create_match(nine_ball, [[players["Alice"]], [players["Bob"]]], ts1)

    alice_9b_rank1 = (await players["Alice"].get_current_rank(nine_ball)).mu
    bob_9b_rank1 = (await players["Bob"].get_current_rank(nine_ball)).mu
    alice_pool_rank1 = (await players["Alice"].get_current_rank(pool_game)).mu
    bob_pool_rank1 = (await players["Bob"].get_current_rank(pool_game)).mu

    assert alice_9b_rank1 > bob_9b_rank1

    # Overall pool ranks should be identical, only 9 ball games have been players
    # so far
    assert alice_9b_rank1 == alice_pool_rank1
    assert bob_9b_rank1 == bob_pool_rank1

    # Match 0 (before match 1): Bob beats Alice in 8 ball
    ts0 = datetime.fromtimestamp(300)
    await create_match(eight_ball, [[players["Bob"]], [players["Alice"]]], ts0)

    alice_9b_rank0 = (await players["Alice"].get_current_rank(nine_ball)).mu
    bob_9b_rank0 = (await players["Bob"].get_current_rank(nine_ball)).mu
    alice_8b_rank0 = (await players["Alice"].get_current_rank(eight_ball)).mu
    bob_8b_rank0 = (await players["Bob"].get_current_rank(eight_ball)).mu
    alice_pool_rank0 = (await players["Alice"].get_current_rank(pool_game)).mu
    bob_pool_rank0 = (await players["Bob"].get_current_rank(pool_game)).mu

    # 9 ball rankings should stay the same
    assert alice_9b_rank1 == alice_9b_rank0
    assert bob_9b_rank1 == bob_9b_rank0

    assert alice_8b_rank0 < bob_8b_rank0

    # Alice's overall pool rank should have dropped from the loss
    assert alice_pool_rank0 < alice_pool_rank1
    # Vice versa for Bob
    assert bob_pool_rank0 > bob_pool_rank1
