from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import jwt

load_dotenv()
app = Flask(__name__)
cors = CORS(app,origins=['*'])
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['WEB_URL'] = os.environ.get('WEB_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['NOW_SHOWING_URL'] = os.environ.get('NOW_SHOWING_URL')
app.config['COMING_SOON_URL'] = os.environ.get('COMING_SOON_URL')
app.config['MOVIE_DETAIL_URL'] = os.environ.get('MOVIE_DETAIL_URL')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app,cors_allowed_origins='*',logger=True,engineio_logger=True)

from backend import view