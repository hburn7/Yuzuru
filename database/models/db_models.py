from datetime import datetime
from peewee import CharField, DateTimeField, IntegerField, \
    BigIntegerField, TextField, ForeignKeyField, IdentityField, \
    BooleanField, DoubleField
from database import YuzuruModel


class User(YuzuruModel):
    id = IdentityField(unique=True)
    user_id = BigIntegerField()
    command_count = IntegerField(default=0)
    spirits = IntegerField(default=0)
    nsfw_age_confirm = BooleanField(default=False)
    nsfw_age_confirm_timestamp = DateTimeField(null=True)
    daily_last_claimed = DateTimeField(null=True)
    timestamp = DateTimeField(default=datetime.utcnow())


class CommandHistory(YuzuruModel):
    id = IdentityField()
    command = CharField()
    options = TextField(null=True)
    timestamp = DateTimeField(default=datetime.utcnow())
    user = ForeignKeyField(User, backref='commands')
    error = BooleanField()
    error_message = TextField(null=True)

    def __repr__(self):
        return f'CommandHistory(id={self.id}, command={self.command}, options={self.options}, user={self.user})'


class GambleHistory(YuzuruModel):
    id = IdentityField()
    game = TextField()
    win = BooleanField(default=False)
    bet = IntegerField()
    payout_multiplier = DoubleField(default=0.0)


class Log(YuzuruModel):
    id = IdentityField()
    guilds = IntegerField()
    users = IntegerField()
    commands = IntegerField()
    timestamp = DateTimeField(default=datetime.utcnow())
