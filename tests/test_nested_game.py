import pytest

from elogate.models import Game
from elogate.errors import NestedGameException


@pytest.mark.asyncio
async def test_db(
    init_db,  # pyright: ignore [reportUnknownParameterType, reportMissingParameterType, reportUnusedParameter]
):
    root_game = Game(name="Root game")
    await root_game.save()

    child_game = Game(name="Child game", parent=root_game)
    await child_game.save()

    try:
        child_child_game = Game(name="Child Child game", parent=child_game)
        await child_child_game.save()
        raise ValueError("Expected a NestedGameException to be thrown")
    except NestedGameException:
        pass
