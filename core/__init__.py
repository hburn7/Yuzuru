from core import config as c


def _get_config():
    return c.get_or_create_config()


# yyyy.mmdd.revision
VERSION = '2022.0813.0'

config = _get_config()
