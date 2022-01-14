from discord.commands import slash_command
from discord.ext import commands


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[931367517564317707])
    async def yuzuru(self, ctx):
        """This is a test description"""
        await ctx.respond("Hey!")


def setup(bot):
    bot.add_cog(Anime(bot))
