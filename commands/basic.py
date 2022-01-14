from discord.commands import slash_command
from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[931367517564317707])
    async def ping(self, ctx):
        """Checks Yuzuru's latency to Discord servers"""
        await ctx.respond(f'🏓 Pong! {ctx.bot.latency * 1000:.2f}ms ')


def setup(bot):
    bot.add_cog(Basic(bot))
