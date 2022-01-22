import logging
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Config:
    token: str
    postgres_username: str
    postgres_pass: str
    postgres_host: str
    postgres_port: int
    postgres_database: str
    docker: bool


def get_or_create_config():
    config_path = Path('./config.ini')
    config = ConfigParser()

    key = "BOT_CONFIG"

    if not config_path.exists():
        logging.info('Config file not found, creating.')
        # Create and return default
        config[key] = {
            "token": "<delete and replace with bot token>",
            "postgres_username": "PostgresUsername",
            "postgres_pass": "PostgresPassword",
            "postgres_host": "localhost",
            "postgres_port": 5432,
            "postgres_database": "Yuzuru",
            "docker": True
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
        return Config(data["token"], data["postgres_username"], data["postgres_pass"],
                      data["postgres_host"], int(data["postgres_port"]), data["postgres_database"], bool(data["docker"]))
