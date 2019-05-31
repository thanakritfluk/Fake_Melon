from app import fake_melon, lm, mongo
from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User

Track = mongo.db.Tracks
Customers = mongo.db.Customers
Play_list = mongo.db.Play_list
Transactions = mongo.db.Transactions
Users = mongo.db.users


@fake_melon.route('/')
def home():
    track_list = Track.find().sort("num_favourite", -1).limit(50)
    name = []
    like = []
    artist = []
    for i in range(50):
        for key, val in track_list.next().items():
            if 'track_name' in key:
                name.append(val)
            if 'num_favourite' in key:
                like.append(val)
            if 'artist' in key:
                artist.append(val)
    return render_template('chart.html', name=name, like=like, artist=artist)


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
            return render_template('login.html', message="Sign up successful", form=form)
    return render_template('regist.html')


@fake_melon.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        searching = request.form['search']
        if searching == "":
            return redirect(url_for('home'))
        else:
            data = Track.find({"track_name": {'$regex': 'Bad', '$options': 'i'}})
            # for i in data:
            #     print(i['track_name'])
            return render_template('display.html', data=data)
    return render_template('display.html')


@lm.user_loader
def load_user(username):
    u = Users.find_one({"username": username})
    if not u:
        return None
    return User(u['username'])
