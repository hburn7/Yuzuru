from core import config as c


def _get_config():
    return c.get_or_create_config()


config = _get_config()
