from app import fake_melon, lm, mongo
from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User
import urllib.request
from bs4 import BeautifulSoup

Track = mongo.db.Tracks
Customers = mongo.db.Customers
Play_list = mongo.db.Play_list
Transactions = mongo.db.Transactions
Users = mongo.db.users


@fake_melon.route('/')
def home():
    track_list = Track.find().sort("num_favourite",-1).limit(50)
    name = []
    like = []
    for i in range (50):
        for key, val in track_list.next().items():
            if 'track_name' in key:
                name.append(val)
            if 'num_favourite' in key:
                like.append(val)
    return render_template('chart.html', name=name, like=like)


@fake_melon.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = Users.find_one({"name": form.username.data})
        if user and User.validate_login(str(user['password']), str(form.password.data)):
            user_obj = User(user['name'])
            print(user_obj)
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("home"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)


@fake_melon.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@fake_melon.route('/song_detail')
def song_detail():
    return render_template('songdetail.html')


@fake_melon.route('/playlist')
@login_required
def playlist():
    return render_template('playlist.html')


@fake_melon.route('/regis')
def registration():
    return render_template('regist.html')


@fake_melon.route('/search')
def search():
    return render_template('display.html')


@lm.user_loader
def load_user(username):
    u = Users.find_one({"name": username})
    if not u:
        return None
    return User(u['name'])
