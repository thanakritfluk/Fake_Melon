from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

fake_melon = Flask(__name__, static_url_path='/app/static')
fake_melon.config.from_object('config')
fake_melon.config['MONGO_DBNAME'] = 'MusicStores'
fake_melon.config['MONGO_URI'] = 'mongodb+srv://admin:1234561%40@cluster0-ngbcy.mongodb.net/MusicStores'
mongo = PyMongo(fake_melon)

lm = LoginManager()
lm.init_app(fake_melon)
lm.login_view = 'login'

from app import views
