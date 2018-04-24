from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

UPLOAD_FOLDER = '/tmp'


app = Flask(__name__, static_url_path="", static_folder="static" )
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'medicalportalprojecta@gmail.com'
app.config['MAIL_PASSWORD'] = 'hyd@12345'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


from app import model
