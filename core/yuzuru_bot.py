import logging
import discord

from datetime import datetime
from discord.ext import tasks
from discord.ext.commands import AutoShardedBot

from database.models.db_models import CommandHistory, User, Log

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass,PyMethodMayBeStatic
class YuzuruBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Start tasks
        self.db_log.start()

    # === EVENTS ===
    async def on_ready(self):
        logger.info("Welcome to Yuzuru!")

    async def on_interaction(self, interaction: discord.Interaction):
        options = interaction.data.get('options')
        if options is not None:
            if 'focused' not in options[0].keys():
                user, created = User.get_or_create(user_id=interaction.user.id)

                User.update({User.command_count: user.command_count + 1}) \
                    .where(User.id == user.id) \
                    .execute()

                ch = CommandHistory(user=user, command=interaction.data.get('name'),
                                    options=interaction.data.get('options'),
                                    timestamp=datetime.utcnow())
                ch.save()
        await super().on_interaction(interaction)

    # === TIMERS ===
    @tasks.loop(seconds=600)
    async def db_log(self):
        guilds = len(self.guilds)
        users = User.select().order_by(User.id.desc()).first()
        commands = CommandHistory.select().order_by(CommandHistory.id.desc()).first()

        # If either users or commands are None, there are no objects in the database.
        # Set to zero if so. Otherwise, use value of id.
        users = users.id if users is not None else 0
        commands = commands.id if commands is not None else 0

        log = Log(guilds=guilds, users=users, commands=commands)
        log.save()
        logger.info(f'Status logged: {log}')

    @db_log.before_loop
    async def await_ready(self):
        # Wait until the bot logs in
        await self.wait_until_ready()
