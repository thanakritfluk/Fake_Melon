from datetime import datetime

import pymongo
from app import fake_melon, lm, mongo
from flask import request, redirect, render_template, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User
import flask_login
from app.api.api_call_method.musixmatch import get_fav_all_year

name_of_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December"]
month = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
currentMonth = datetime.now().month
currentYear = datetime.now().year
Track = mongo.db.Tracks
Customers = mongo.db.Customers
Play_list = mongo.db.Play_list
Transactions = mongo.db.Transactions
Users = mongo.db.users


def find_rank(track_name):
    count = 0
    for i in Track.find().sort('num_favourite', pymongo.DESCENDING):
        count += 1
        if i['track_name'] == track_name:
            return count


@fake_melon.route('/')
def home():
    track_list = Track.find().sort(
        [("num_favourite", pymongo.DESCENDING)]).limit(50)
    like_user = None
    fav_user = None
    like_list = []
    fav_list = []
    if flask_login.current_user.is_authenticated():
        name = Users.find_one({"username": flask_login.current_user.get_id()})
        for key, val in name.items():
            if '_id' in key:
                c_user = Play_list.find_one({"_id": val})
                if c_user is not None:
                    for key, val in c_user.items():
                        if 'playlist' in key:
                            fav_user = val
                        if 'likes' in key:
                            like_user = val
        for key, val in fav_user.items():
            fav_list.append(val)
        for key, val in like_user.items():
            like_list.append(val)
    return render_template('chart.html', data=track_list, fav=fav_list, like=like_list)


@fake_melon.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = Users.find_one({"username": form.username.data})
        if user and User.validate_login(str(user['password']), str(form.password.data)):
            user_obj = User(user['username'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("home"))
        flash("Wrong username or password!", category='error Cup')
    return render_template('login.html', title='login', form=form, error="Error Nama")


@fake_melon.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@fake_melon.route('/song_detail', methods=['POST'])
def song_detail():
    name = request.form['name']
    rank = find_rank(str(name))
    track_detail = Track.find_one({"track_name": name})
    like_user = None
    fav_user = None
    like_list = []
    fav_list = []
    if flask_login.current_user.is_authenticated():
        name = Users.find_one({"username": flask_login.current_user.get_id()})
        for key, val in name.items():
            if '_id' in key:
                c_user = Play_list.find_one({"_id": val})
                if c_user is not None:
                    for key, val in c_user.items():
                        if 'playlist' in key:
                            fav_user = val
                        if 'likes' in key:
                            like_user = val
        for key, val in fav_user.items():
            fav_list.append(val)
        for key, val in like_user.items():
            like_list.append(val)
    return render_template('songdetail.html', data=track_detail, rank=rank, fav=fav_list, like=like_list)


@fake_melon.route('/playlist')
@login_required
def playlist():

    track_list = Track.find().sort([("num_favourite", pymongo.DESCENDING)])
    fav_user = None
    fav_list = []
    t_list = []
    if flask_login.current_user.is_authenticated():
        name = Users.find_one({"username": flask_login.current_user.get_id()})
        for key, val in name.items():
            if '_id' in key:
                c_user = Play_list.find_one({"_id": val})
                if c_user is not None:
                    for key, val in c_user.items():
                        if 'playlist' in key:
                            fav_user = val
        for key, val in fav_user.items():
            fav_list.append(val)
        for i in Track.find().sort('num_favourite', pymongo.DESCENDING):
            if i['track_name'] in fav_list:
                t_list.append(i)

    return render_template('playlist.html', track=t_list)


@fake_melon.route('/fav', methods=['POST'])
@login_required
def fav():
    s_name = request.form['name']
    search = request.form['search']
    name = Users.find_one({"username": flask_login.current_user.get_id()})
    id = 0
    for key, val in name.items():
        if '_id' in key:
            id = val
    tmp = Play_list.find_one({"_id": id})
    tmp1 = None
    if tmp is not None:
        for key, val in tmp.items():
            if 'playlist' in key:
                tmp1 = val
        if tmp1 is not None:
            maximum = 0
            for key, val in tmp1.items():
                if int(key) > maximum:
                    maximum = int(key)
            size = maximum + 1
            st = "playlist.{size}".format(size=size)
            Play_list.update_one({'_id': id}, {"$set": {st: s_name}})
        else:
            Play_list.insert_one({
                "_id": id,
                "playlist": {"1": s_name},
                "likes": {}
            })
    else:
        Play_list.insert_one({
            "_id": id,
            "playlist": {"1": s_name},
            "likes": {}
        })
    if search == '.':
        return redirect(url_for('home'))
    elif search == ',':
        rank = find_rank(str(s_name))
        track_detail = Track.find_one({"track_name": s_name})
        like_user = None
        fav_user = None
        like_list = []
        fav_list = []
        if flask_login.current_user.is_authenticated():
            name = Users.find_one({"username": flask_login.current_user.get_id()})
            for key, val in name.items():
                if '_id' in key:
                    c_user = Play_list.find_one({"_id": val})
                    if c_user is not None:
                        for key, val in c_user.items():
                            if 'playlist' in key:
                                fav_user = val
                            if 'likes' in key:
                                like_user = val
            for key, val in fav_user.items():
                fav_list.append(val)
            for key, val in like_user.items():
                like_list.append(val)
        return render_template('songdetail.html', data=track_detail, rank=rank, fav=fav_list, like=like_list)
    else:
        if search == "":
            return redirect(url_for('home'))
        else:
            like_user = None
            fav_user = None
            like_list = []
            fav_list = []
            if flask_login.current_user.is_authenticated():
                name = Users.find_one(
                    {"username": flask_login.current_user.get_id()})
                for key, val in name.items():
                    if '_id' in key:
                        c_user = Play_list.find_one({"_id": val})
                        if c_user is not None:
                            for key, val in c_user.items():
                                if 'playlist' in key:
                                    fav_user = val
                                if 'likes' in key:
                                    like_user = val
                for key, val in fav_user.items():
                    fav_list.append(val)
                for key, val in like_user.items():
                    like_list.append(val)
            data = Track.find(
                {"track_name": {'$regex': str(search), '$options': 'i'}})
            return render_template('display.html', searching=search, data=data, like=like_list, fav=fav_list)
        return render_template('display.html')


@fake_melon.route('/like', methods=['POST'])
@login_required
def like():
    s_name = request.form['name']
    search = request.form['search']
    name = Users.find_one({"username": flask_login.current_user.get_id()})
    id = 0
    for key, val in name.items():
        if '_id' in key:
            id = val
    tmp = Play_list.find_one({"_id": id})
    tmp1 = None
    if tmp is not None:
        for key, val in tmp.items():
            if 'likes' in key:
                tmp1 = val
        if tmp1 is not None:
            maximum = 0
            for key, val in tmp1.items():
                if int(key) > maximum:
                    maximum = int(key)
            size = maximum + 1
            st = "likes.{size}".format(size=size)
            Play_list.update_one({'_id': id}, {"$set": {st: s_name}})
        else:
            Play_list.insert_one({
                "_id": id,
                "playlist": {},
                "likes": {"1": s_name}
            })
    else:
        Play_list.insert_one({
            "_id": id,
            "playlist": {},
            "likes": {"1": s_name}
        })
    track_detail = Track.find_one({"track_name": s_name})
    like = 0
    for key, val in track_detail.items():
        if 'num_favourite' in key:
            like = int(val)
    like += 1
    Track.update_one({"track_name": s_name}, {
                     "$set": {"num_favourite": int(like)}})
    if search == '.':
        return redirect(url_for('home'))
    elif search == ',':
        rank = find_rank(str(s_name))
        track_detail = Track.find_one({"track_name": s_name})
        like_user = None
        fav_user = None
        like_list = []
        fav_list = []
        if flask_login.current_user.is_authenticated():
            name = Users.find_one({"username": flask_login.current_user.get_id()})
            for key, val in name.items():
                if '_id' in key:
                    c_user = Play_list.find_one({"_id": val})
                    if c_user is not None:
                        for key, val in c_user.items():
                            if 'playlist' in key:
                                fav_user = val
                            if 'likes' in key:
                                like_user = val
            for key, val in fav_user.items():
                fav_list.append(val)
            for key, val in like_user.items():
                like_list.append(val)
        return render_template('songdetail.html', data=track_detail, rank=rank, fav=fav_list, like=like_list)
    else:
        if search == "":
            return redirect(url_for('home'))
        else:
            like_user = None
            fav_user = None
            like_list = []
            fav_list = []
            if flask_login.current_user.is_authenticated():
                name = Users.find_one(
                    {"username": flask_login.current_user.get_id()})
                for key, val in name.items():
                    if '_id' in key:
                        c_user = Play_list.find_one({"_id": val})
                        if c_user is not None:
                            for key, val in c_user.items():
                                if 'playlist' in key:
                                    fav_user = val
                                if 'likes' in key:
                                    like_user = val
                for key, val in fav_user.items():
                    fav_list.append(val)
                for key, val in like_user.items():
                    like_list.append(val)
            data = Track.find(
                {"track_name": {'$regex': str(search), '$options': 'i'}})
            return render_template('display.html', searching=search, data=data, like=like_list, fav=fav_list)
        return render_template('display.html')


@fake_melon.route('/registration', methods=['POST', 'GET'])
def registration():
    form = LoginForm()
    if request.method == "POST":
        display_name = request.form['display_name']
        username = request.form['username']
        password = request.form['password']
        if Users.count_documents({"username": username}) != 0:
            return render_template('regist.html', error="User name already exits")
        else:
            _id = Users.insert_one({
                "display_name": display_name,
                "username": username,
                "password": password
            })
            insert_id = _id.inserted_id
            Play_list.insert_one({
                "_id": insert_id,
                "playlist": {},
                "likes": {}
            })
            return redirect(url_for('login'))
    return render_template('regist.html')


@fake_melon.route('/remove', methods=['POST'])
@login_required
def remove():
    if request.method == "POST":
        s_name = request.form['name']
        name = Users.find_one({"username": flask_login.current_user.get_id()})
        id = 0
        for key, val in name.items():
            if '_id' in key:
                id = val
                c_user = Play_list.find_one({"_id": val})
                if c_user is not None:
                    for key, val in c_user.items():
                        if 'playlist' in key:
                            fav_user = val
        s = 0
        for key, val in fav_user.items():
            if s_name in val:
                s = key
        st = "playlist.{size}".format(size=s)

        Play_list.update_one({'_id': id}, {"$unset": {st: s_name}})
    return redirect(url_for('playlist'))


@fake_melon.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        searching = request.form['search']
        if searching == "":
            return redirect(url_for('home'))
        else:
            like_user = None
            fav_user = None
            like_list = []
            fav_list = []
            if flask_login.current_user.is_authenticated():
                name = Users.find_one(
                    {"username": flask_login.current_user.get_id()})
                for key, val in name.items():
                    if '_id' in key:
                        c_user = Play_list.find_one({"_id": val})
                        if c_user is not None:
                            for key, val in c_user.items():
                                if 'playlist' in key:
                                    fav_user = val
                                if 'likes' in key:
                                    like_user = val
                for key, val in fav_user.items():
                    fav_list.append(val)
                for key, val in like_user.items():
                    like_list.append(val)
            data = Track.find(
                {"track_name": {'$regex': str(searching), '$options': 'i'}})
            return render_template('display.html', searching=searching, data=data, like=like_list, fav=fav_list)
    return render_template('display.html')


def chart_data(field):
    bar_labels = []
    bar_values = []
    for key, value in get_fav_all_year(currentYear, field).items():
        if key == "NONE":
            key = "Other"
        bar_labels.append(key)
        bar_values.append(value)
    return bar_labels, bar_values


@fake_melon.route("/chart")
def chart():
    genre_labels, genre_values = chart_data("genre")
    genre_max = max(genre_values)
    artist_labels, artist_values = chart_data("artist_name")
    artist_max = max(artist_values)
    return render_template('bar_chart.html', title='Genre and Artist popular of ' + str(currentYear),
                           genre_max=genre_max + 2, genre_labels=genre_labels,
                           genre_values=genre_values, artist_max=artist_max + 2, artist_labels=artist_labels,
                           artist_values=artist_values)


@lm.user_loader
def load_user(username):
    u = Users.find_one({"username": username})
    if not u:
        return None
    return User(u['username'])
