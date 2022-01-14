import logging
import discord
import peewee
from discord.ext.commands import AutoShardedBot

from datetime import datetime

from database import db
from database.models.db_models import CommandHistory, User


# noinspection PyAbstractClass,PyMethodMayBeStatic
class YuzuruBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logging.info("Welcome to Yuzuru!")

    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.is_command():
            pass

        user, created = User.get_or_create(user_id=interaction.user.id)

        ch = CommandHistory(user=user, command=interaction.data.get('name'),
                            options=interaction.data.get('options'),
                            timestamp=datetime.utcnow())
        ch.save()
        await super().on_interaction(interaction)

