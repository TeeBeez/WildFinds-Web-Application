from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from flask_login import login_user, login_required, logout_user
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    name = request.form.get('name', '').strip()
    password = request.form.get('password', '').strip()
    city = request.form.get('city','').strip()
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # Validate that all fields are filled
    if not all([username, email, name, password, city]):
        flash("All fields are required.", "error")
        return redirect(url_for('auth.signup'))  # Reload the signup page

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        if existing_user.email == email:
            flash("Email already in use. Please log in.", "error")
            return redirect(url_for('auth.login'))  # Redirect to login page
        elif existing_user.username == username:
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for('auth.signup'))  # Reload the signup page

    try:
        new_user = User(email=email, username=username, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'), city=city, latitude=latitude, longitude=longitude)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('main.profile'))
    except Exception as e:
        flash('Error Occurred, please try again.')
        return redirect(url_for('auth.signup'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
