from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from . import db

# Change directory to wildfinds-app-folder, then type in python setup_db.py in terminal to update/create database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(1000))

    gender = db.Column(db.String(10), nullable=True)  # Example: 'Male', 'Female', 'Other'
    city = db.Column(db.String(100), nullable=True) 
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    age = db.Column(db.Integer, nullable=True)  

    # Relationship to Post model if each user can create multiple posts
    posts = db.relationship('Post', backref='user', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_metadata = db.Column(JSON)  # Store metadata as JSON
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    city_posted_in = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"