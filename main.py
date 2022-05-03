import logging
import logging.config
import datetime

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


setup_logger()

import sys
import discord
import time

from database import db
from database.models.db_models import User, CommandHistory, GambleHistory, Log
from commands import anime, basic, games, custom
from core import config
from core.yuzuru_bot import YuzuruBot

logger = logging.getLogger('main')
logger.debug("Logger initialized.")


def main():
    # Init DB -- reconnect on failure
    while True:
        logger.debug(f'Attempting database connection...')
        try:
            db.connect()
            logger.debug(f'Connected to database!')
            db.create_tables([User, CommandHistory, GambleHistory, Log])
            break
        except Exception as e:
            logger.critical(f'Failed to establish a database connection. Retrying...')
            logger.debug(f'Exception info: {e}')
            time.sleep(2)

    # Configure bot
    bot = YuzuruBot(intents=discord.Intents.all())

    # Register all cogs
    anime.setup(bot)
    basic.setup(bot)
    games.setup(bot)
    custom.setup(bot)

    try:
        bot.run(config.token)
    except discord.LoginFailure:
        logger.critical("--- Failed to launch Yuzuru. Is your token correct? (check config.ini) ---")
        sys.exit(1)


if __name__ == '__main__':
    main()
