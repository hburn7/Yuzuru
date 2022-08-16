import logging
from pathlib import Path

import discord
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd
from discord import slash_command, Option
from discord.ext import commands

from core.yuzuru_bot import YuzuruContext
from database.models.db_models import CommandHistory, Log

logger = logging.getLogger(__name__)


def _get_fname(sector, user_id):
    p = Path('./stats')
    if not p.exists():
        p.mkdir()

    return f'stats/{sector}--{user_id}.png'


def _command_data():
    data = CommandHistory.select()

    amounts = {}
    errors = {}

    for cmd in data:
        name = cmd.command
        error = cmd.error

        if name in amounts.keys():
            amounts[name] += 1
        else:
            amounts[name] = 1

        if name in errors.keys() and error:
            errors[name] += 1
        elif name not in errors.keys() and not error:
            errors[name] = 0
        else:
            errors[name] = 1

    d = {
        'Name': amounts.keys(),
        'Amount': [x for x in amounts.values()],
        'Error': [x for x in errors.values()]
    }

    return pd.DataFrame(d).sort_values(by=['Amount'], ascending=False)


def _save_command_chart(df: pd.DataFrame, fname):
    df.groupby(['Amount', 'Error']).size()
    df.plot(kind='bar', x='Name', stacked=True)

    plt.title('Yuzuru Commands')
    plt.xlabel('Command Name')
    plt.ylabel('Executions')
    plt.legend(labels=['Successful Executions', 'Errors'])
    plt.tight_layout()
    return plt.savefig(fname=fname, format='png')


def _historical_data():
    data = Log.select()

    d = {'time': [], 'commands': [], 'users': [], 'guilds': []}

    for log in data:
        d['time'].append(log.timestamp)
        d['commands'].append(log.commands)
        d['users'].append(log.users)
        d['guilds'].append(log.guilds)

    return pd.DataFrame(d).sort_values(by=['time'])


def _save_historical_chart(df: pd.DataFrame, fname):
    gs = gridspec.GridSpec(2, 2)

    plt.figure()

    ax_users = plt.subplot(gs[0, 0])
    ax_guilds = plt.subplot(gs[0, 1])
    ax_commands = plt.subplot(gs[1, :])

    df.plot(kind='line', x='time', y='users', ax=ax_users)
    df.plot(kind='line', x='time', y='guilds', ax=ax_guilds)
    df.plot(kind='line', x='time', y='commands', ax=ax_commands)

    plt.title('Yuzuru Historical Data')
    plt.tight_layout()
    return plt.savefig(fname=fname, format='png')


stats_endpoints = ['command', 'historical']


def _stats_endpoints(ctx: discord.AutocompleteContext):
    return [x for x in stats_endpoints if x.startswith(ctx.value.lower())]


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def stats(self, ctx: YuzuruContext,
                    sector: Option(str, "Which stats do you want to see?", autocomplete=_stats_endpoints)):
        fname = _get_fname(sector, ctx.user.id)

        await ctx.defer()

        if sector == 'command':
            data = _command_data()
            _save_command_chart(data, fname)
            await ctx.respond(file=discord.File(fname))
        elif sector == 'historical':
            data = _historical_data()
            _save_historical_chart(data, fname)
            await ctx.respond(file=discord.File(fname))

        Path(fname).unlink()


def setup(bot):
    bot.add_cog(Stats(bot))
