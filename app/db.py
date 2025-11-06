import os
import sqlite3
import click
from datetime import datetime

from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    exists = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='database_version'").fetchone()
    if exists is None:
        print("No version table found, creating.")
        with current_app.open_resource(os.path.normcase('db/create-version-table.sql')) as f:
            db.executescript(f.read().decode('utf8'))

    database_version = db.execute("SELECT version FROM database_version").fetchone()['version']
    print(f'Current database version: {database_version}')
    while True:
        next_version = database_version + 1
        migration_filename = os.path.normcase(current_app.root_path) + os.path.normcase(f'/db/migrations/{next_version}.sql')
        print("Looking for migration file:", migration_filename)
        if not os.path.exists(os.path.normcase(migration_filename)):
            break

        print("Applying migration:", migration_filename)
        with current_app.open_resource(migration_filename) as f:
            db.executescript(f.read().decode('utf8'))
        db.execute(
            "UPDATE database_version SET version = ?",
            (next_version,)
        )
        db.commit()
        database_version = next_version

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)