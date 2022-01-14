import logging
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Config:
    token: str


def get_or_create_config():
    logger.critical("This is a test of config.py")
    config_path = Path('./config.ini')
    config = ConfigParser()

    key = "BOT_CONFIG"

    if not config_path.exists():
        logging.info('Config file not found, creating.')
        # Create and return default
        config[key] = {
            "token": "<delete and replace with bot token>"
        }
        with open(config_path.absolute(), 'w') as conf:
            config.write(conf)
        logging.info('Successfully created new config file.')
        config.read(config_path.absolute())
        data = config[key]
        return Config(data["token"])
    else:
        # Return existing
        config.read(config_path.absolute())
        data = config[key]
        return Config(data["token"])
