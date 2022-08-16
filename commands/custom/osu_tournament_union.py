import csv
import os

import discord
import io
from discord import slash_command
from discord.ext import commands
from typing import List

from core.text.yuzuru_embed import YuzuruEmbed
from core.yuzuru_bot import YuzuruContext


guild_id = 1006209366753546301


class OsuTournamentUnion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @slash_command(guild_ids=[guild_id])
    # async def foo(self, ctx: YuzuruContext):
    #     pass

def setup(bot):
    bot.add_cog(OsuTournamentUnion(bot))
