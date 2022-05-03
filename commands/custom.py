import discord
from discord import slash_command
from discord.ext import commands

from core.text.yuzuru_embed import YuzuruEmbed
from core.yuzuru_bot import YuzuruContext


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[968216369529245726])
    async def stt3_paste(self, ctx: YuzuruContext, team_name: str, tag_paste: str):
        """Creates a team role and applies it to all users in the team,
        only if all users from the paste exist in the discord."""

        embed = YuzuruEmbed()
        description = ''

        # Check if everyone is present
        valid = True
        search = [x.strip() for x in tag_paste.split(' ')]

        found_users = []
        for name in search:
            match = ctx.guild.get_member_named(name)
            if match is None:
                description += f'❌ {name} is not in the server!\n'
                valid = False
            else:
                description += f'✅ {match.mention} is present.\n'
                found_users.append(match)

        if not valid:
            embed.title = 'Team creation failed! (Missing members)'
            description += 'The missing members must join the server ' \
                           'before team creation may occur.'

            embed.description = description
            await ctx.respond(embed=embed)
            return

        await ctx.respond(f'Users validated, creating team {team_name}...')
        team_role = await ctx.guild.create_role(name=team_name, color=discord.Color.blurple(), mentionable=True)

        # Force role on the bottom, just to be sure.
        positions = {
            team_role: 1
        }

        await ctx.guild.edit_role_positions(positions=positions)

        # Give captain role to first user.
        captain = found_users[0]
        stt3_player_role = ctx.guild.get_role(968224711144267896)
        stt3_captain_role = ctx.guild.get_role(968224654252703834)

        description += f'\nDenoted {captain.mention} as captain.'

        await captain.add_roles(stt3_captain_role)

        # Add team role and STT3 player role if found.
        for user in found_users:
            try:
                await user.add_roles(team_role, stt3_player_role)
            except Exception as e:
                await ctx.respond(f'Failed to add role {team_role} to {user} -- {e}')

        embed.description = description
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Custom(bot))
