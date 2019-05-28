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
    return render_template('home.html')


@fake_melon.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = Users.find_one({"name": form.username.data})
        if user and User.validate_login(str(user['password']), str(form.password.data)):
            user_obj = User(user['name'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("write"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)


@fake_melon.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@fake_melon.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    return render_template('write.html')


@fake_melon.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')


@lm.user_loader
def load_user(username):
    u = Users.find_one({"name": username})
    if not u:
        return None
    return User(u['name'])
