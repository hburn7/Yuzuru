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

    @slash_command(guild_ids=[968216369529245726])
    async def stt3_paste(self, ctx: YuzuruContext, team_name: str, tag_paste: str):
        """Creates a team role and applies it to all users in the team,
        only if all users from the paste exist in the discord."""

        await ctx.defer()
        old_team_name = team_name
        team_name = f'STT3 Team: {old_team_name}'

        embed = YuzuruEmbed()
        description = ''

        # Check if everyone is present
        valid = True

        found_users = []
        for name in get_tags(tag_paste):
            if name == '' or name is None:
                continue

            match = ctx.guild.get_member_named(name)
            if match is None:
                description += f'❌ {name} is not in the server!\n'
                valid = False
            else:
                description += f'✅ {match.mention} is present.\n'
                found_users.append(match)

        if not valid:
            embed.title = f'Team creation failed! ({old_team_name})'
            description += 'The missing members must join the server ' \
                           'before team creation may occur.'

            embed.description = description
            embed.color = discord.Color.red()
            await ctx.respond(embed=embed)
            return

        team_role = None

        found = False
        for role in ctx.guild.roles:
            if role.name == team_name:
                team_role = role
                found = True
                break

        if not found:
            team_role = await ctx.guild.create_role(name=team_name, color=discord.Color.blurple(), mentionable=False)

        # Force role on the bottom, just to be sure.
        positions = {
            team_role: 1
        }

        await ctx.guild.edit_role_positions(positions=positions)

        # Give captain role to first user.
        captain = found_users[0]
        stt3_player_role = ctx.guild.get_role(968224711144267896)
        stt3_captain_role = ctx.guild.get_role(968224654252703834)
        stt3_fa_role = ctx.guild.get_role(972226684675825694)

        description += f'\nDenoted {captain.mention} as captain of {team_role.mention}.'

        await captain.add_roles(stt3_captain_role)

        # Add team role and STT3 player role if found.
        for user in found_users:
            try:
                await user.add_roles(team_role, stt3_player_role)
            except Exception as e:
                await ctx.respond(f'Failed to add role {team_role} to {user} -- {e}')

            # Remove Free Agent role
            try:
                await user.remove_roles(stt3_fa_role)
            except Exception as e:
                await ctx.respond(f'Failed to remove role {team_role} from {user} -- {e}')

        embed.title = f'Team Creation Success: {old_team_name}'
        embed.description = description
        await ctx.respond(embed=embed)

    @commands.command(guild_ids=[968216369529245726])
    async def stt3_verify(self, ctx: commands.Context):
        """Verifies all users from all teams are in the discord"""

        if not ctx.message.attachments:
            await ctx.send("Please upload the STT3 Admin 'Reg Responses' sheet as a `.csv` file attachment.")
            return

        uid = ctx.message.author.id
        if not uid == 146092837723832320 and not uid == 289792596287553538:
            await ctx.send("You lack permissions to execute this command.")
            return

        # noinspection PyTypeChecker
        await ctx.message.attachments.pop().save(fp='tmp.csv')
        await ctx.message.delete()

        roles = ctx.guild.roles

        with open('tmp.csv', mode='r') as file:
            csvFile = csv.DictReader(file)
            for row in csvFile:
                team = Team(row)

                matches = list(filter(lambda x: team.name.lower() in x.name.lower(), roles))

                if not matches:
                    await ctx.send(f'Manual review required - associated role not found.\n```diff\n- {team}```')
                    continue
                else:
                    role = matches[0]

                missing = team.check_presence(ctx)

                if not missing:
                    continue

                embed = YuzuruEmbed()
                description = ''
                # if not missing:
                #     embed.title = f'Team Verified ({team.name})'
                #     description = f'✅ {role.mention} is not missing any players.'
                # else:
                #     embed.title = f'Team Verification Failed! ({team.name})'
                #
                #     for m in missing:
                #         description += f'❌ {m} not found.\n'

                embed.title = f'Team Verification Failed! ({team.name})'

                description += f'Associated Role: {role.mention}\n\n'

                for m in missing:
                    description += f'❌ {m} is missing.\n'

                embed.description = description
                await ctx.send(embed=embed)

        os.remove('tmp.csv')
        await ctx.send('**Verification complete. Users found above, if any, will be '
                       'screened out if they are not in the Discord when registrations close.**')
        return


class Team:
    def __init__(self, d):
        self.d = d
        self.name = d['Team Name'].strip()
        self.captain = d['(Captain) Player 1 Discord Tag'].strip()
        self.player_discord_tags = [self.captain, *self.__get_discord_content__()]

    def check_presence(self, ctx: commands.Context) -> List[str]:
        def present(tag):
            return ctx.guild.get_member_named(tag) is not None

        not_present = []

        for t in self.player_discord_tags:
            if not present(t):
                not_present.append(t)

        return not_present

    def __get_discord_headers__(self):
        return [f'Player {x} Discord Tag' for x in range(2, 7)]

    def __get_discord_content__(self):
        headers = self.__get_discord_headers__()

        r = []
        for h in headers:
            tag = self.d[h].strip()

            if tag is not None and tag is not '':
                r.append(tag)

        return r

    def __repr__(self):
        return f'Team(name={self.name}, captain={self.captain}, players={self.player_discord_tags})'




def setup(bot):
    bot.add_cog(Custom(bot))
    # bot.add_command(Custom.stt3_verify)
