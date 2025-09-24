from enum import Enum

from openskill.models import MODELS as RANKING_MODELS
from tortoise.exceptions import ConfigurationError
from tortoise.expressions import Q
from tortoise.models import Model
from tortoise.transactions import in_transaction
from tortoise.fields import (
    CharField,
    IntField,
    DatetimeField,
    JSONField,
    ForeignKeyField,
    ManyToManyField,
    FloatField,
)

from elogate.errors import NestedGameException

RankingModels = Enum("RankingModels", {cls.__name__: cls for cls in RANKING_MODELS})
CHAR_FIELD_LEN_NAMES = 256


class EnumField(CharField):
    """
    An example extension to CharField that serializes Enums
    to and from a str representation in the DB.
    """

    def __init__(self, enum_type: type[Enum], max_length: int | None = None, **kwargs):
        if max_length is None:
            max_length = max([len(v.name) for v in enum_type])
        super().__init__(max_length=max_length, **kwargs)
        if not issubclass(enum_type, Enum):
            raise ConfigurationError("{} is not a subclass of Enum!".format(enum_type))
        self._enum_type = enum_type

    def to_db_value(self, value: Enum, instance) -> str:
        return value.name

    def to_python_value(self, value: str) -> Enum:
        try:
            # This doesn't work sometimes for some reason
            # return self._enum_type(value)
            return getattr(self._enum_type, value)
        except Exception:
            raise ValueError(
                "Database value {} does not exist on Enum {}.".format(
                    value, self._enum_type
                )
            )


class Player(Model):
    id = IntField(primary_key=True)
    name = CharField(max_length=CHAR_FIELD_LEN_NAMES, unique=True)

    async def get_current_rank(self, game: "Game") -> "PlayerRank":
        out = await self.ranks.filter(game=game).order_by("-match__timestamp").first()
        return out


class PlayerRank(Model):
    id = IntField(primary_key=True)
    match = ForeignKeyField("elogate.Match", related_name="ranks")
    game = ForeignKeyField("elogate.Game", related_name="ranks")
    player = ForeignKeyField("elogate.Player", related_name="ranks")
    # Rank in the match, same values mean players were on the same team
    rank_idx = IntField()
    mu = FloatField()
    sigma = FloatField()


# TODO: is this even needed? Might be nice for autofilling teams but beyond that idk
# class Team(Model):
#    id = IntField(primary_key=True)
#    name = CharField(max_length=CHAR_FIELD_LEN_NAMES)
#    game = ForeignKeyField("elogate.Game", related_name="teams")
#    members = ManyToManyField(
#        "elogate.Player", related_name="teams", through="player_team"
#    )


class Match(Model):
    id = IntField(primary_key=True)
    timestamp = DatetimeField(auto_now_add=True, unique=True)
    modified = DatetimeField(auto_now=True)
    game = ForeignKeyField("elogate.Game", related_name="matches")
    participants = JSONField()

    def __repr__(self) -> str:
        # TODO: is there a way to getting the game repr without needing await
        return f"<Match: ({self.game}) ts: {self.timestamp} [{self.id}]>"


class Game(Model):
    id = IntField(primary_key=True)
    name = CharField(max_length=CHAR_FIELD_LEN_NAMES, unique=True)
    ranking_model = EnumField(
        enum_type=RankingModels,
        default=RankingModels.PlackettLuce,
        max_length=CHAR_FIELD_LEN_NAMES,
    )
    # TODO: custom encoder/decoder?
    ranking_model_args = JSONField(default={})
    parent = ForeignKeyField("elogate.Game", related_name="children", null=True)

    async def save(self, *args, **kwargs):
        async def _raise_on_fail(_mark):
            if _mark.parent and await _mark.children.all():
                raise NestedGameException("Child game cannot have its own children")

        async def _check_children(_mark):
            for child in await _mark.children.all():
                _raise_on_fail(child)
                _check_children(child)

        async with in_transaction():

            await super().save(*args, **kwargs)

            # Check all parents for invalid rows
            mark = self
            while mark.parent:
                await _raise_on_fail(mark)
                mark = mark.parent

            await _check_children(self)

    @property
    def all_matches(self):
        return Match.filter(Q(game=self) | Q(game__parent=self)).order_by("timestamp")

    def __repr__(self) -> str:
        return f"<Game: '{self.name}' [{self.id}]>"
