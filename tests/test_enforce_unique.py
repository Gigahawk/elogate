import pytest
from tortoise.exceptions import IntegrityError

from elogate.models import Game, Player


@pytest.mark.asyncio
async def test_enforce_unique(
    init_db,  # pyright: ignore [reportUnknownParameterType, reportMissingParameterType, reportUnusedParameter]
):
    game1 = Game(name="Game")
    await game1.save()

    game2 = Game(name="Game")
    try:
        await game2.save()
        raise ValueError("Saving two games with the same name should fail")
    except IntegrityError:
        pass

    player1 = Player(name="Player")
    await player1.save()

    player2 = Player(name="Player")
    try:
        await player2.save()
        raise ValueError("Saving two players with the same name should fail")
    except IntegrityError:
        pass
