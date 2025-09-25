from typing import override, TypeAlias
from collections.abc import Iterable
from datetime import datetime

import openskill.models as ranking_models

# from tortoise.exceptions import ConfigurationError
from tortoise.expressions import Q
from tortoise.models import Model
from tortoise.transactions import (
    in_transaction,  # pyright: ignore [reportUnknownVariableType]
)
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.fields import (
    Field,
    CharField,
    IntField,
    DatetimeField,
    JSONField,
    ForeignKeyField,
    ForeignKeyRelation,
    ForeignKeyNullableRelation,
    ReverseRelation,
    FloatField,  # pyright: ignore [reportUnknownVariableType]
)

from elogate.errors import NestedGameException, PlayerUnrankedException


# TODO: is there a better way to do this?
RankingModelsType: TypeAlias = (
    type[ranking_models.BradleyTerryFull]
    | type[ranking_models.BradleyTerryPart]
    | type[ranking_models.PlackettLuce]
    | type[ranking_models.ThurstoneMostellerFull]
    | type[ranking_models.ThurstoneMostellerPart]
)
RankingModelsRatingType: TypeAlias = (
    type[ranking_models.BradleyTerryFullRating]
    | type[ranking_models.BradleyTerryPartRating]
    | type[ranking_models.PlackettLuceRating]
    | type[ranking_models.ThurstoneMostellerFullRating]
    | type[ranking_models.ThurstoneMostellerPartRating]
)
RankingModels = {cls.__name__: cls for cls in ranking_models.MODELS}

CHAR_FIELD_LEN_NAMES = 256


class Player(Model):
    id: Field[int] = IntField(primary_key=True)
    name: Field[str] = CharField(max_length=CHAR_FIELD_LEN_NAMES, unique=True)

    ranks: ReverseRelation[  # pyright: ignore [reportUninitializedInstanceVariable]
        "PlayerRank"
    ]

    async def get_current_rank(self, game: "Game") -> "PlayerRank":
        out = await self.ranks.filter(game=game).order_by("-match__timestamp").first()
        if out is None:
            raise PlayerUnrankedException
        return out


class PlayerRank(Model):
    id: Field[int] = IntField(primary_key=True)
    match: ForeignKeyRelation["Match"] = ForeignKeyField(
        "elogate.Match", related_name="ranks"
    )
    game: ForeignKeyRelation["Game"] = ForeignKeyField(
        "elogate.Game", related_name="ranks"
    )
    player: ForeignKeyRelation[Player] = ForeignKeyField(
        "elogate.Player", related_name="ranks"
    )
    # Rank in the match, same values mean players were on the same team
    rank_idx: Field[int] = IntField()
    mu: Field[float] = FloatField()
    sigma: Field[float] = FloatField()


# TODO: is this even needed? Might be nice for autofilling teams but beyond that idk
# class Team(Model):
#    id = IntField(primary_key=True)
#    name = CharField(max_length=CHAR_FIELD_LEN_NAMES)
#    game = ForeignKeyField("elogate.Game", related_name="teams")
#    members = ManyToManyField(
#        "elogate.Player", related_name="teams", through="player_team"
#    )


class Match(Model):
    id: Field[int] = IntField(primary_key=True)
    timestamp: Field[datetime] = DatetimeField(auto_now_add=True, unique=True)
    modified: Field[datetime] = DatetimeField(auto_now=True)
    game: ForeignKeyRelation["Game"] = ForeignKeyField(
        "elogate.Game", related_name="matches"
    )
    participants: Field[list[list[int]]] = JSONField()
    ranks: ReverseRelation[  # pyright: ignore [reportUninitializedInstanceVariable]
        PlayerRank
    ]

    @override
    def __repr__(self) -> str:
        # TODO: is there a way to getting the game repr without needing await
        return f"<Match: ({self.game}) ts: {self.timestamp} [{self.id}]>"


class Game(Model):
    id: Field[int] = IntField(primary_key=True)
    name: Field[str] = CharField(max_length=CHAR_FIELD_LEN_NAMES, unique=True)
    ranking_model_name: Field[str] = CharField(
        max_length=CHAR_FIELD_LEN_NAMES, default="PlackettLuce"
    )
    # TODO: custom encoder/decoder?
    ranking_model_args: Field[dict[str, object]] = JSONField(default={})
    parent: ForeignKeyNullableRelation["Game"] = ForeignKeyField(
        "elogate.Game", related_name="children", null=True
    )
    children: ReverseRelation[  # pyright: ignore [reportUninitializedInstanceVariable]
        "Game"
    ]

    @property
    def ranking_model(self) -> RankingModelsType:
        return RankingModels[self.ranking_model_name]

    async def _enforce_no_nesting(self):
        async def _raise_on_fail(_mark: "Game"):
            if _mark.parent and await _mark.children.all():
                raise NestedGameException("Child game cannot have its own children")

        async def _check_children(_mark: "Game"):
            for child in await _mark.children.all():
                await _raise_on_fail(child)
                await _check_children(child)

        # Check all parents for invalid rows
        mark = self
        while mark.parent:
            await _raise_on_fail(mark)
            mark = mark.parent

        await _check_children(self)

    async def _enforce_valid_ranking_model(self):
        # TODO: validate args?
        assert self.ranking_model_name in RankingModels.keys()

    @override
    async def save(
        self,
        using_db: BaseDBAsyncClient | None = None,
        update_fields: Iterable[str] | None = None,
        force_create: bool = False,
        force_update: bool = False,
    ):
        async with in_transaction():
            await super().save(
                using_db=using_db,
                update_fields=update_fields,
                force_create=force_create,
                force_update=force_update,
            )
            await self._enforce_no_nesting()
            await self._enforce_valid_ranking_model()

    @property
    def all_matches(self):
        return Match.filter(Q(game=self) | Q(game__parent=self)).order_by("timestamp")

    @override
    def __repr__(self) -> str:
        return f"<Game: '{self.name}' [{self.id}]>"
