import logging
from datetime import datetime, timedelta
from typing import Optional

import discord
from discord import Option

from core.yuzuru_bot import YuzuruContext, YuzuruEmbed
from discord.commands import slash_command
from discord.ext import commands
from discord.ext.commands import has_guild_permissions, bot_has_guild_permissions, guild_only

from database.models.db_models import User, Log

logger = logging.getLogger(__name__)


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def invite(self, ctx: YuzuruContext):
        link = 'https://discord.com/api/oauth2/authorize?client_id=408046042244841474&permissions=1496125140054&scope=bot%20applications.commands'
        discord = 'https://discord.gg/GkFR4xGKMM'
        github = 'https://github.com/hburn7/Yuzuru'
        embed = YuzuruEmbed()
        embed.title = "Yuzuru Invite Links"
        embed.description = f'Invite Yuzuru: {link}\nDiscord Server: {discord}\nGithub Repository: {github}'
        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command()
    async def ping(self, ctx: YuzuruContext):
        """Checks Yuzuru's latency to Discord servers"""
        await ctx.respond(f'🏓 Pong! {ctx.bot.latency * 1000:.2f}ms ')

    @slash_command()
    @has_guild_permissions(manage_roles=True)
    @bot_has_guild_permissions(manage_roles=True)
    async def create_roles(self, ctx: YuzuruContext, roles: str, mentionable: Optional[bool] = True):
        """Creates one role per comma-separated phrase."""
        await ctx.defer()
        separated = roles.split(',')
        added = []
        failed = []
        for name in separated:
            try:
                role = await ctx.guild.create_role(name=name.strip(), reason=f'Created via Yuzuru /create_roles (executed by {ctx.user})')
                added.append(role)
            except Exception as e:
                failed.append(name)
                logger.warning(f'Failed to create role {name} in guild {ctx.guild}')

        embed = YuzuruEmbed()
        embed.title = 'Create Roles'
        embed.description = f'**Created Roles:** {[x.mention for x in added]} (Mentionable -> {mentionable})'

        if failed:
            embed.description += f'\n**Failed to Create Roles:** ' + str(failed)
            embed.color = discord.Color.red()

        await ctx.respond(embed=embed)

    @slash_command()
    @has_guild_permissions(manage_roles=True)
    @bot_has_guild_permissions(manage_roles=True)
    async def delete_roles(self, ctx: YuzuruContext, *roles):
        """Deletes all roles listed"""
        await ctx.defer()
        deleted = []
        error = []
        for role in roles:
            if not isinstance(role, discord.Role):
                error.append((role, f'{role} is not a role.'))
                continue

            try:
                await role.delete(reason=f'Yuzuru /delete_roles (invoked by {ctx.user})')
                deleted.append(role.name)
            except Exception as e:
                error.append((role, e))

        embed = YuzuruEmbed()
        embed.title = 'Delete Roles'
        embed.description = f'**Deleted Roles:** {deleted}'

        if error:
            embed.description += f'\n**Failed to Delete Roles:** ' + str([f'{x} -> {y}' for x, y in error])
            embed.color = discord.Color.red()

        await ctx.respond(embed=embed)

    @slash_command()
    @has_guild_permissions(manage_roles=True)
    @bot_has_guild_permissions(manage_roles=True)
    async def cleanup_roles(self, ctx: YuzuruContext):
        """Deletes ALL roles that are not being used by any users"""
        roles = filter(lambda r: not r.members, ctx.guild.roles)

        await ctx.defer()

        deleted = []
        failed = []
        for role in roles:
            if not role.members:
                try:
                    await role.delete(reason=f'Yuzuru /cleanup_roles executed by {ctx.user}')
                    deleted.append(role.name)
                    logger.debug(f'Deleted role {role} from guild {ctx.guild} (cleanup_roles)')
                except Exception as e:
                    logger.debug(f'Failed to delete role {e} from guild {ctx.guild} during cleanup_roles execution',
                                 exc_info=e)
                    failed.append(role.name)

        embed = YuzuruEmbed()
        embed.title = 'Role Cleanup'

        if deleted:
            embed.description = f'**Deleted Roles:** {deleted}'

        if failed:
            embed.description += f'\n**Failed to Delete:** {failed}'

        if not deleted and not failed:
            embed.description = f'There are no roles to be deleted.'

        await ctx.respond(embed=embed)

    @slash_command()
    async def daily(self, ctx: YuzuruContext):
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

    @slash_command()
    @has_guild_permissions(manage_messages=True)
    @bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx: YuzuruContext, amount: int):
        try:
            channel = ctx.channel
            messages = await ctx.channel.history(limit=amount).flatten()
            await channel.delete_messages(messages)
            await ctx.respond('Done')
        except Exception as e:
            await ctx.respond(f'Error: {e}')

    def emote_str(self, added):
        res = 'Added emotes: '
        for emoji in added:
            if emoji.animated:
                res += f'<a:{emoji.name}:{emoji.id}>'
            else:
                res += f'<:{emoji.name}:{emoji.id}>'
        return res

    @slash_command()
    @has_guild_permissions(manage_emojis=True)
    @bot_has_guild_permissions(manage_emojis=True)
    async def steal(self, ctx: YuzuruContext, emojis: str):
        """'Steals' all emotes from a message and adds them to the server. Bot must share the emote server"""
        await ctx.defer()
        emojis = emojis.replace('><', '> <')
        splits = emojis.split(' ')
        added = []

        for emoji in splits:
            emoji = emoji.strip()
            if emoji == '':
                continue

            # Example: <:argeseal:971495260465287188>
            try:
                animated = emoji.startswith('<a:')
                if animated:
                    emoji = emoji.replace('<a:', '<:')

                name = emoji.split('<:')[1].split(':')[0]
                emoji_id = int(emoji.split(':')[-1].split('>')[0])
                client_emoji = ctx.bot.get_emoji(emoji_id)

                if not client_emoji:
                    continue

                emoji_bytes = await client_emoji.read()
                new = await ctx.guild.create_custom_emoji(name=name, image=emoji_bytes, reason='Added via Yuzuru /steal')
                logger.info(f'Stolen emoji {new.name} and added to guild {ctx.guild}')
                added.append(new)
            except Exception as e:
                logger.warning(f'Failed to steal emoji', exc_info=e)
                if ctx.bot.is_ws_ratelimited():
                    if added:
                        await ctx.respond(f'We are being rate limited. Process interrupted.')
                        await ctx.respond(self.emote_str(added))
                    else:
                        await ctx.respond(f'We are being rate limited. Failed to add any emotes.')
            finally:
                continue

        if added:
            await ctx.respond(self.emote_str(added))
        else:
            await ctx.respond('Failed to add emotes')


def setup(bot):
    bot.add_cog(Basic(bot))
