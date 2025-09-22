from enum import Enum

from openskill.models import MODELS as RANKING_MODELS
from tortoise.exceptions import ConfigurationError
from tortoise.models import Model
from tortoise.fields import (
    CharField,
    IntField,
    DatetimeField,
    JSONField,
    ForeignKeyField,
    ManyToManyField,
    FloatField,
)

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
            return self._enum_type(value)
        except Exception:
            raise ValueError(
                "Database value {} does not exist on Enum {}.".format(
                    value, self._enum_type
                )
            )


class Player(Model):
    id = IntField(primary_key=True)
    name = CharField(max_length=CHAR_FIELD_LEN_NAMES, unique=True)


class PlayerRank(Model):
    id = IntField(primary_key=True)
    match = ForeignKeyField("elogate.Match", related_name="ranks")
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


class Game(Model):
    id = IntField(primary_key=True)
    name = CharField(max_length=CHAR_FIELD_LEN_NAMES, unique=True)
    ranking_model = EnumField(enum_type=RankingModels, max_length=CHAR_FIELD_LEN_NAMES)
    # TODO: custom encoder/decoder?
    ranking_model_args = JSONField()


class Match(Model):
    id = IntField(primary_key=True)
    modified = DatetimeField(auto_now=True)
    game = ForeignKeyField("elogate.Game", related_name="matches")
