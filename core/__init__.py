from core import config as c


def _get_config():
    return c.get_or_create_config()


VERSION = '1.0-a30.01.2022'

config = _get_config()
