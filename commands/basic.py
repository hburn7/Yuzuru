import logging
from datetime import datetime, timedelta

from core.yuzuru_bot import YuzuruContext
from discord.commands import slash_command
from discord.ext import commands
from discord.ext.commands import has_guild_permissions, bot_has_guild_permissions

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

    @slash_command()
    @has_guild_permissions(manage_messages=True)
    @bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx: YuzuruContext, amount: int):
        try:
            channel = ctx.channel
            messages = await ctx.channel.history(limit=amount).flatten()
            await channel.delete_messages(messages)
            await ctx.respond('Done')
        except e:
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
