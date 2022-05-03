import anime_images_api
import discord
import nekos
import random

from pathlib import Path

from discord import Option
from discord.commands import slash_command
from discord.ext import commands

from core import config
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


def load_paths_from_source(d):
    """
    Loads absolute file paths into a list from a given directory.
    :param d: Source directory
    :return: None if empty, List[str] if any files are found.
    """
    if d == '':
        return None

    path = Path(d)
    if not path.exists():
        raise FileNotFoundError(f'Directory {d} does not exist.')

    if not path.is_dir():
        raise NotADirectoryError(f'{d} is not a directory.')

    ret = []
    for f in path.iterdir():
        ret.append(f.absolute())

    return ret


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = anime_images_api.Anime_Images()

        self.neko_images = None
        self.lewd_images = None
        self.nsfw_images = None

        # Try to read images from config directories. Leave empty if not found.
        if config.has_neko_dir:
            self.neko_images = load_paths_from_source(config.neko_dir)

        if config.has_lewd_dir:
            self.lewd_images = load_paths_from_source(config.lewd_dir)

        if config.has_nsfw_dir:
            self.nsfw_images = load_paths_from_source(config.nsfw_dir)

    @slash_command()
    async def owoify(self, ctx, text: str):
        """OwO-ify's your text"""
        await ctx.respond(nekos.owoify(text))

    @slash_command()
    async def gif(self, ctx: discord.ApplicationContext,
                  action: Option(str, "Pick an action!", autocomplete=get_sfw_endpoints),
                  user: Option(discord.User, "Target someone with your message.", required=False)):
        """Sends a gif into chat based on the selected action"""
        embed = YuzuruEmbed()
        plural = sfw_plural.get(action)
        if user:
            description = f'{ctx.user.mention} {plural} you!'
        else:
            description = f'{ctx.user.mention} {plural} the air!'

        embed.description = description
        embed.set_image(url=self.api.get_sfw(action))

        if user:
            await ctx.respond(user.mention, embed=embed)
        else:
            await ctx.respond(embed=embed)

    @slash_command()
    async def nsfw(self, ctx, num: Option(int, "Number of images to send en masse.", min_value=1, max_value=10, default=1)):
        """Sends an NSFW image / gif into the chat (requires NSFW channel)"""
        if not await ctx.nsfw_check():
            return

        await ctx.nsfw_age_confirm()
        await ctx.defer()

        if num > 10 or num < 1:
            await ctx.respond('Number of images must be between 1 and 10.', ephemeral=True)
            return

        if self.nsfw_images:
            for i in range(num):
                path = random.choice(self.nsfw_images)
                await ctx.respond(file=discord.File(path))
        else:
            for i in range(num):
                embed = YuzuruEmbed()
                embed.set_image(url=self.api.get_nsfw('hentai'))
                await ctx.respond(embed=embed)

    @slash_command()
    async def lewd(self, ctx, num: Option(int, "Number of images to send en masse.", min_value=1, max_value=10, default=1)):
        if not await ctx.nsfw_check():
            return

        await ctx.nsfw_age_confirm()
        
        await ctx.defer()
        if self.lewd_images:
            for i in range(num):
                path = random.choice(self.lewd_images)
                await ctx.respond(file=discord.File(path))
        else:
            await ctx.respond(f'Whoops! Something went wrong. (No lewds)', ephemeral=True)

    @slash_command()
    async def neko(self, ctx, num: Option(int, "Number of images to send en masse.", min_value=1, max_value=10, default=1)):
        """Sends a picture of a cute cat into chat"""
        if self.neko_images:
            for i in range(num):
                path = random.choice(self.neko_images)
                await ctx.respond(file=discord.File(path))
        else:
            # Rely on API as fallback
            for i in range(num):
                embed = YuzuruEmbed()
                embed.set_image(url=nekos.cat())
                await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Anime(bot))
