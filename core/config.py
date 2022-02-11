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

    neko_dir: str
    lewd_dir: str
    nsfw_dir: str

    has_neko_dir: bool
    has_lewd_dir: bool
    has_nsfw_dir: bool


def path_valid(p):
    return p != '' and Path(p).exists()


def get_or_create_config():
    config_path = Path('./config.ini')

    logger.debug(f'Searching for config file at {config_path.absolute()}...')

    config = ConfigParser()

    bot_key = "BOT_CONFIG"
    data_key = "DATA"

    if not config_path.exists():
        logger.debug('Config file not found, creating...')
        # Create and return default
        config[bot_key] = {
            "token": "YOUR_TOKEN_HERE",
            "postgres_username": "postgres",
            "postgres_pass": "password",
            "postgres_host": "localhost",
            "postgres_port": 5500,
            "postgres_database": "yuzuru",
            "docker": False
        }
        config[data_key] = {
            "neko_dir": "",
            "lewd_dir": "",
            "nsfw_dir": ""
        }

        with open(config_path.absolute(), 'w') as conf:
            config.write(conf)
        logger.debug(f'Successfully created new config file at {config_path.absolute()}.')

    # Return existing / newly created log
    logger.debug(f'Configuration file found.')
    config.read(config_path.absolute())
    bot_data = config[bot_key]
    data_data = config[data_key]

    has_neko_dir = path_valid(data_data["neko_dir"])
    has_lewd_dir = path_valid(data_data["lewd_dir"])
    has_nsfw_dir = path_valid(data_data["nsfw_dir"])

    neko_path = str(Path(data_data["neko_dir"]).absolute()) if has_neko_dir else None
    lewd_path = str(Path(data_data["lewd_dir"]).absolute()) if has_lewd_dir else None
    nsfw_path = str(Path(data_data["nsfw_dir"]).absolute()) if has_nsfw_dir else None

    return Config(bot_data["token"], bot_data["postgres_username"], bot_data["postgres_pass"],
                  bot_data["postgres_host"], int(bot_data["postgres_port"]), bot_data["postgres_database"],
                  bot_data["docker"] == "True", neko_dir=neko_path, lewd_dir=lewd_path, nsfw_dir=nsfw_path,
                  has_neko_dir=has_neko_dir, has_lewd_dir=has_lewd_dir, has_nsfw_dir=has_nsfw_dir)
