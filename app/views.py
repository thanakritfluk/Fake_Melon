from app import fake_melon, lm, mongo
from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User
import flask_login
import bson

Track = mongo.db.Tracks
Customers = mongo.db.Customers
Play_list = mongo.db.Play_list
Transactions = mongo.db.Transactions
Users = mongo.db.users


@fake_melon.route('/')
def home():
    track_list = Track.find().sort("num_favourite", -1).limit(50)
    like_user = None
    fav_user = None
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
    link = []
    name = []
    like = []
    artist = []
    lc = []
    fc = []
    for i in range(50):
        for key, val in track_list.next().items():
            if 'track_name' in key:
                name.append(val)
                if  like_user is not None:
                    if val in like_user:
                        lc.append(1)
                    else:
                        lc.append(0)
                else:
                    lc.append(0)
                if  fav_user is not None:
                    if val in fav_user:
                        fc.append(1)
                    else:
                        fc.append(0)
                else:
                    fc.append(0)
                print("val= ", val)
                print("fav_user= ", fav_user)
                print(val in fav_user)
            if 'num_favourite' in key:
                like.append(val)
            if 'artist' in key:
                artist.append(val)
            if 'music_url' in key:
                link.append(val)

    return render_template('chart.html', name=name, like=like, artist=artist, lc=lc, fc=fc, link=link)


@fake_melon.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = Users.find_one({"username": form.username.data})
        if user and User.validate_login(str(user['password']), str(form.password.data)):
            user_obj = User(user['username'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            print(user_obj.username)
            return redirect(request.args.get("next") or url_for("home"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)

@fake_melon.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@fake_melon.route('/song_detail', methods=['POST'])
def song_detail():
    name = request.form['name']
    rank = request.form['rank']
    artist = 'not found'
    genre = 'not found'
    albums = 'not found'
    like = '0'
    img = 'static/image/notfound.jpg'
    track_detail = Track.find_one({"track_name": name})
    for key, val in track_detail.items():
        if 'track_name' in key:
            name = val
        if 'num_favourite' in key:
            like = val
        if 'artist_name' in key:
            artist = val
        if 'genre' in key:
            genre = val
        if 'albums_name' in key:
            albums = val
        if 'url_img' in key:
            img = val
    return render_template('songdetail.html', name=name, like=like, artist=artist, genre=genre, albums=albums, img=img,
                           rank=rank)

@fake_melon.route('/playlist')
@login_required
def playlist():
    return render_template('playlist.html')

@fake_melon.route('/fav', methods=['POST'])
@login_required
def fav():
    s_name = request.form['name']
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
            size = maximum+1
            st = "playlist.{size}".format(size=size)
            Play_list.update_one({'_id': id},{"$set" :{st: s_name}})
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
    return redirect(url_for('home'))

@fake_melon.route('/like', methods=['POST'])
@login_required
def like():
    s_name = request.form['name']
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
            size = maximum+1
            st = "likes.{size}".format(size=size)
            Play_list.update_one({'_id': id},{"$set" :{st: s_name}})
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
            like = val
    like += 1
    Track.update_one({"track_name": s_name},{"$set" :{"num_favourite": str(like)}})
    return redirect(url_for('home'))

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
                "list": {}
            })
            return render_template('login.html', message="Sign up successful", form=form)
    return render_template('regist.html')

@fake_melon.route('/search')
def search():
    return render_template('display.html')


@lm.user_loader
def load_user(username):
    u = Users.find_one({"username": username})
    if not u:
        return None
    return User(u['username'])

