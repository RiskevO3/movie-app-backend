from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
cors = CORS(app,origins=['*'])
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['WEB_URL'] = os.environ.get('WEB_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['NOW_SHOWING_URL'] = os.environ.get('NOW_SHOWING_URL')
app.config['COMING_SOON_URL'] = os.environ.get('COMING_SOON_URL')
app.config['MOVIE_DETAIL_URL'] = os.environ.get('MOVIE_DETAIL_URL')
app.config['MOVIE_TICKET_URL'] = os.environ.get('MOVIE_TICKET_URL')
app.config['MOVIE_MEDIA_URL'] =  os.environ.get('MOVIE_MEDIA_URL')
app.config['DEBUG'] = os.environ.get('DEBUG')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from backend import view