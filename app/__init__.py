from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__, static_url_path="", static_folder="static" )
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
# app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import model
