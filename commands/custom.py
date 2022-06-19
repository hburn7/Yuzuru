import csv
import os

import discord
import io
from discord import slash_command
from discord.ext import commands
from typing import List

from core.text.yuzuru_embed import YuzuruEmbed
from core.yuzuru_bot import YuzuruContext


def get_tags(paste):
    if '\t' in paste:
        return [x.strip() for x in paste.split('\t')]
    else:
        return [x.strip() for x in paste.split(' ')]


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Server-specific commands live here

def setup(bot):
    bot.add_cog(Custom(bot))
    # bot.add_command(Custom.stt3_verify)
