from enum import unique
from tortoise.models import Model
from tortoise import fields


class Player(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255, unique=True)


class Game(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255, unique=True)


class Match(Model):
    id = fields.IntField(primary_key=True)
