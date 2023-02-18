from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_script._compat import text_type
from config import Config
from datetime import timedelta, date, datetime, time

app = Flask(__name__)
app.config.from_object(Config)


app.permanent_session_lifetime = timedelta(minutes=60)
db = SQLAlchemy(app)
app.secret_key = "e_voting"

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)