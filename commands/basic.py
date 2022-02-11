import logging
from datetime import datetime, timedelta

from discord.commands import slash_command
from discord.ext import commands

from database.models.db_models import User

logger = logging.getLogger(__name__)


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def ping(self, ctx):
        """Checks Yuzuru's latency to Discord servers"""
        await ctx.respond(f'🏓 Pong! {ctx.bot.latency * 1000:.2f}ms ')

    @slash_command()
    async def daily(self, ctx):
        """Claim 500 spirits (24h cooldown)"""
        cooldown_hrs = 24
        amount = 500

        user, created = User.get_or_create(user_id=ctx.user.id)
        stamp = datetime.utcnow()
        if user.daily_last_claimed and user.daily_last_claimed > stamp - timedelta(hours=cooldown_hrs):
            time_remaining = timedelta(hours=cooldown_hrs) - (stamp - user.daily_last_claimed)
            time_str = str(time_remaining).split('.')[0]
            await ctx.respond(f'You have already claimed your daily bonus. Try again in `{time_str}`.')
        else:
            user.daily_last_claimed = stamp
            user.spirits += amount
            user.save()

            logger.info(f'User {user} claimed daily spirits. They now have {user.spirits} (+{amount}).')
            await ctx.respond(f'Successfully claimed daily spirits! You now have {user.spirits} spirits.')


def setup(bot):
    bot.add_cog(Basic(bot))
