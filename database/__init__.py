from peewee import PostgresqlDatabase, Model

from core import config


def get_db():
    user = config.postgres_username
    pw = config.postgres_pass
    host = config.postgres_host
    port = config.postgres_port
    db_name = config.postgres_database
    docker = config.docker

    if docker:
        connection_str = f'postgresql://{user}:{pw}@db/{db_name}'
    else:
        connection_str = f'postgresql://{user}:{pw}@{host}:{port}/{db_name}'
    psql_db = PostgresqlDatabase(connection_str)
    return psql_db


db = get_db()


class YuzuruModel(Model):
    class Meta:
        database = db
