import logging
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


def get_or_create_engine():
    engine = create_engine('sqlite:///yuzuru.db')

    if not database_exists(engine.url):
        create_database(engine.url)

        logging.info(f'Created new database at url {engine.url}')
    return engine


engine = get_or_create_engine()
