import logging
import logging.config
import datetime
import core

from pathlib import Path

from utils.log_formatter import LogFormatter


# Configure logger first thing -- other imports rely on a configured logger before main() would set it up.
def setup_logger():
    formatter = LogFormatter()
    s = datetime.datetime.utcnow()
    path = Path('./logs')
    file = f'{path.absolute()}/yuzuru_{s.year}-{s.month}-{s.day}-{s.hour}{s.minute}{s.second}.log'

    # Create log directory if it doesn't exist
    if not path.exists():
        path.mkdir()

    # Log to file...
    logging.basicConfig(filename=file, format=formatter.log_fmt, level=logging.DEBUG)

    # Log to console as well...
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(LogFormatter())
    logging.getLogger('').addHandler(console)

    # Suppress library debug logs
    logging.getLogger('discord.client').setLevel(logging.INFO)
    logging.getLogger('discord.gateway').setLevel(logging.INFO)
    logging.getLogger('matplotlib').setLevel(logging.INFO)

    if not core.config.debug:
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('peewee').setLevel(logging.INFO)


setup_logger()

import sys
import discord
import time

from database import db
from database.models.db_models import User, CommandHistory, GambleHistory, Log
from commands import anime, basic, games, stats
from commands.custom import osu_tournament_union
from core import config
from core.yuzuru_bot import YuzuruBot

logger = logging.getLogger(__name__)
logger.info("Logger initialized.")


def main():
    # Init DB -- reconnect on failure
    while True:
        logger.info(f'Attempting database connection...')
        try:
            db.connect()
            logger.info(f'Connected to database!')
            db.create_tables([User, CommandHistory, GambleHistory, Log])
            break
        except Exception as e:
            logger.critical(f'Failed to establish a database connection. Retrying...')
            logger.info(f'Exception info: {e}')
            time.sleep(2)

    # Configure bot
    bot = YuzuruBot(intents=discord.Intents.all(), command_prefix='!')

    # Register all cogs
    anime.setup(bot)
    basic.setup(bot)
    games.setup(bot)
    stats.setup(bot)

    # Custom cogs
    osu_tournament_union.setup(bot)

    try:
        bot.run(config.token)
    except discord.LoginFailure:
        logger.critical("--- Failed to launch Yuzuru. Is your token correct? (check config.ini) ---")
        sys.exit(1)


if __name__ == '__main__':
    main()
