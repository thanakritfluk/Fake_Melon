from flask import Flask, render_template, request
from flask_pymongo import PyMongo, MongoClient

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'MusicStores'
app.config["MONGO_URI"] = "mongodb+srv://admin:1234561%40@cluster0-ngbcy.mongodb.net/MusicStores"
mongo = PyMongo(app)
# All collections in database
Track = mongo.db.Tracks
Customers = mongo.db.Customers
Play_list = mongo.db.Play_list
Transactions = mongo.db.Transactions


@app.route('/')
def index():
    return 'OK!'

# def add():
#     # user = mongo.db.Tracks
#     data = mongo.db.Tracks.find_one()
#     print(data)
#     # user.insert_one({'name': 'fluk'})
#     return 'Added user'


if __name__ == '__main__':
    app.run()
