import logging
from datetime import datetime

import discord
from discord import ApplicationContext, DiscordException
from discord.ext import tasks
from discord.ext.commands import AutoShardedBot

import views
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
                user.nsfw_age_confirm = True
                user.nsfw_age_confirm_timestamp = datetime.utcnow()
                user.save()
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

    async def on_application_command_completion(self, context: YuzuruContext):
        # Update user command count
        user, created = User.get_or_create(user_id=context.user.id)
        user.command_count += 1
        user.save()

        # Add command history and log
        ch = CommandHistory(user=user, command=context.command.name,
                            options=context.interaction.data.get('options'),
                            timestamp=datetime.utcnow(), error=False, error_message=None)
        ch.save()
        logger.info(f'{repr(ch)} -- User {user.id} has now used {user.command_count} commands')

    async def on_application_command_error(self, context: YuzuruContext, exception: DiscordException):
        user, created = User.get_or_create(user_id=context.user.id)
        ch = CommandHistory(user=user, command=context.command.name,
                            options=context.interaction.data.get('options'),
                            timestamp=datetime.utcnow(), error=True, error_message=exception.args)
        ch.save()
        logger.info(f'Command error from user {user.user_id} [database id={user.id}] when executing {ch.command}: {exception}')

    # 5WC Specific
    async def on_member_join(self, member: discord.User):
        if member.guild.id == 999513842872766514:
            channel = self.get_channel(999514169764229200)  # 5WC #welcome chat
            await channel.send(f'👋 **{member}** has joined.')

    async def on_member_remove(self, member: discord.User):
        if member.guild.id == 999513842872766514:
            channel = self.get_channel(999514169764229200)  # 5WC #welcome chat
            await channel.send(f'🚶 **{member}** has left.')

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

        log = Log(guilds=guilds, users=users, commands=commands, timestamp=datetime.utcnow())
        log.save()
        logger.info(f'Status logged: {log}')

    @db_log.before_loop
    async def await_ready(self):
        # Wait until the bot logs in
        await self.wait_until_ready()
