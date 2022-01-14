import discord
import datetime
import logging
import logging.config

from commands import anime
from utils.logformatter import LogFormatter
from pathlib import Path


def main():
    # Configure logger
    formatter = LogFormatter()
    s = datetime.datetime.now()
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

    # Configure bot
    bot = discord.AutoShardedBot()

    # Register all cogs
    anime.setup(bot)

    @bot.event
    async def on_ready():
        logging.info("Welcome to Yuzuru!")

    try:
        from core import config
        bot.run(config.token)
    except discord.LoginFailure:
        logging.critical("--- Failed to launch Yuzuru. Is your token correct? (check config.ini) ---")


if __name__ == '__main__':
    main()
