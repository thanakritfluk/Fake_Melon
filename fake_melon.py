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


def get_data(collection):
    return collection.find_one()


# EX. query = { "address": {"$regex": "^S"} }
def delete_data(collection, query):
    return collection.delete_many(query)


# Ex. myquery = { "address": { "$regex": "^S" } }
#     newvalues = { "$set": { "name": "Minnie" } }
def update_data(collection, query, new_value):
    return collection.update_many(query, new_value)


@fake_melon.route('/')
def index():
    print(get_data(Track)['track_name'])
    return 'OK!'


# def add():
#     # user = mongo.db.Tracks
#     data = mongo.db.Tracks.find_one()
#     print(data)
#     # user.insert_one({'name': 'fluk'})
#     return 'Added user'


if __name__ == '__main__':
    fake_melon.run()
