from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import find_dotenv, load_dotenv
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap5(app)
bcrypt = Bcrypt(app)

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)
