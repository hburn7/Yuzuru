from datetime import datetime
from peewee import CharField, DateTimeField, IntegerField, BigIntegerField, TextField, ForeignKeyField, IdentityField
from database import YuzuruModel


class User(YuzuruModel):
    id = IdentityField(unique=True)
    command_count = IntegerField(default=0)
    timestamp = DateTimeField(default=datetime.utcnow())
    user_id = BigIntegerField()


class CommandHistory(YuzuruModel):
    id = IdentityField()
    command = CharField()
    options = TextField(null=True)
    timestamp = DateTimeField(default=datetime.utcnow())
    user = ForeignKeyField(User, backref='commands')


