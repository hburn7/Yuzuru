import logging
from peewee import PostgresqlDatabase, Model

from core import config


def get_db():
    user = config.postgres_username
    pw = config.postgres_pass
    host = config.postgres_host
    port = config.postgres_port
    db_name = config.postgres_database

    psql_db = PostgresqlDatabase(f'postgresql://{user}:{pw}@{host}:{port}/{db_name}')
    return psql_db


db = get_db()


class YuzuruModel(Model):
    class Meta:
        database = db
