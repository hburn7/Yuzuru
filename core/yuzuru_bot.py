import logging
import discord

import views

from datetime import datetime
from discord import ApplicationContext
from discord.ext import tasks
from discord.ext.commands import AutoShardedBot, Context

from core.text.yuzuru_embed import YuzuruEmbed
from database.models.db_models import CommandHistory, User, Log

logger = logging.getLogger(__name__)


class YuzuruContext(ApplicationContext):

    async def nsfw_check(self):
        if not self.channel.is_nsfw():
            await self.respond('This command may only be executed in NSFW channels.', ephemeral=True)
            return False
        return True

    async def nsfw_age_confirm(self):
        user, created = User.get_or_create(user_id=self.user.id)

        if not user.nsfw_age_confirm:
            embed = YuzuruEmbed()
            view = views.Confirm()
            embed.description = f'{self.user.mention} Hold on a sec! Are you 18 or older and wish to view NSFW content?'
            await self.respond(embed=embed, view=view, ephemeral=True)
            await view.wait()

            # We do not need to send confirmation / cancellation messages due to
            # how the view handles it already.
            if view.value:
                User.update({User.nsfw_age_confirm: True, User.nsfw_age_confirm_timestamp: datetime.utcnow()}) \
                    .where(User.id == user.id) \
                    .execute()
            else:
                return


# noinspection PyAbstractClass,PyMethodMayBeStatic
class YuzuruBot(AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Start tasks
        self.db_log.start()

    # Context
    async def get_application_context(self, interaction, cls=YuzuruContext):
        return await super().get_application_context(interaction, cls=cls)

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
