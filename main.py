import sys

import discord
import datetime
import logging
import logging.config
import time

from pathlib import Path

from database import db
from database.models.db_models import User, CommandHistory, Log
from commands import anime, basic
from core import config
from core.yuzuru_bot import YuzuruBot
from utils.log_formatter import LogFormatter


def main():
    # Configure logger
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

    # Init DB -- reconnect on failure
    while True:
        try:
            db.connect()
            db.create_tables([CommandHistory, User, Log])
            break
        except Exception as e:
            logging.critical(f'Failed to establish a database connection. Retrying...')
            logging.debug(f'Exception info: {e}')
            time.sleep(2)

    # Configure bot
    bot = YuzuruBot()

    # Register all cogs
    anime.setup(bot)
    basic.setup(bot)

    try:
        bot.run(config.token)
    except discord.LoginFailure:
        logging.critical("--- Failed to launch Yuzuru. Is your token correct? (check config.ini) ---")
        sys.exit(1)


if __name__ == '__main__':
    main()
