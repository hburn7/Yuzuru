from peewee import CharField, DateTimeField, BigIntegerField, TextField, ForeignKeyField, IdentityField
from database import YuzuruModel


class User(YuzuruModel):
    id = IdentityField()
    user_id = BigIntegerField()


class CommandHistory(YuzuruModel):
    id = IdentityField()
    command = CharField()
    options = TextField(null=True)
    timestamp = DateTimeField()
    user = ForeignKeyField(User, backref='commands')


