import anime_images_api
import discord
import nekos
import typing

from discord import Option
from discord.commands import slash_command
from discord.ext import commands

from core.text.yuzuru_embed import YuzuruEmbed

sfw_endpoints = ['hug', 'kiss', 'slap', 'wink', 'pat', 'kill', 'cuddle']
nsfw_endpoints = ['boobs', 'hentai']

sfw_plural = {
    'hug': 'hugged',
    'kiss': 'kissed',
    'slap': 'slapped',
    'wink': 'winked',
    'pat': 'patted',
    'kill': 'killed',
    'cuddle': 'cuddled'
}


def get_sfw_endpoints(ctx: discord.AutocompleteContext):
    return [x for x in sfw_endpoints if x.startswith(ctx.value.lower())]


def get_nsfw_endpoints(ctx: discord.AutocompleteContext):
    return [x for x in nsfw_endpoints if x.startswith(ctx.value.lower())]


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = anime_images_api.Anime_Images()

    @slash_command(guild_ids=[931367517564317707])
    async def neko(self, ctx):
        """Sends a picture of a cute cat into chat"""
        embed = YuzuruEmbed()
        embed.set_image(url=nekos.cat())
        await ctx.respond(embed=embed)

    @slash_command(guild_ids=[931367517564317707])
    async def owoify(self, ctx, text: str):
        """OwO-ify's your text"""
        await ctx.respond(nekos.owoify(text))

    @slash_command(guild_ids=[931367517564317707])
    async def gif(self, ctx: discord.ApplicationContext,
                  action: Option(str, "Pick an action!", autocomplete=get_sfw_endpoints),
                  user: Option(discord.User, "Target someone with your message.")):
        """Sends a gif into chat based on the selected action"""
        embed = YuzuruEmbed()
        plural = sfw_plural.get(action)
        if user:
            description = f'{user.mention} {ctx.user.mention} {plural} you!'
        else:
            description = f'{ctx.user.mention} {plural} the air!'

        embed.set_image(url=self.api.get_sfw(action))
        await ctx.respond(description, embed=embed)

    @slash_command(guild_ids=[931367517564317707])
    async def nsfw(self, ctx: discord.ApplicationContext,
                   action: Option(str, "Pick a type of NSFW to receive.", autocomplete=get_nsfw_endpoints)):
        """Sends an NSFW gif into the chat"""
        embed = YuzuruEmbed()
        embed.set_image(url=self.api.get_nsfw(action))
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Anime(bot))
