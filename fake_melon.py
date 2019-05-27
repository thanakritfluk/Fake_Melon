from flask import Flask, render_template, request
from flask_pymongo import PyMongo, MongoClient

fake_melon = Flask(__name__)

fake_melon.config['MONGO_DBNAME'] = 'MusicStores'
fake_melon.config["MONGO_URI"] = "mongodb+srv://admin:1234561%40@cluster0-ngbcy.mongodb.net/MusicStores"
mongo = PyMongo(fake_melon)
# All collections in database
Track = mongo.db.Tracks
Customers = mongo.db.Customers
Play_list = mongo.db.Play_list
Transactions = mongo.db.Transactions


@fake_melon.route('/')
def index():
    return 'OK!'


# def add():
#     # user = mongo.db.Tracks
#     data = mongo.db.Tracks.find_one()
#     print(data)
#     # user.insert_one({'name': 'fluk'})
#     return 'Added user'


if __name__ == '__main__':
    fake_melon.run()
