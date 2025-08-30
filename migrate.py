from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app, db  # Make sure your app and db are imported properly

migrate = Migrate(app, db)

# Required for Flask CLI to register commands
from flask.cli import with_appcontext
import click

@app.cli.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo("Initialized the database.")

