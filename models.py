from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(140))
    email = db.Column(db.String(140))
    password = db.Column(db.String(140))
    password_hash = db.Column(db.String(140))
    trips = db.relationship('Trip',backref='user',lazy='dynamic')
  
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tripname = db.Column(db.String(140))
    speed = db.Column(db.Float(precision=2),nullable=False)
    distance = db.Column(db.Float(precision=2),nullable=False)
    elevation = db.Column(db.Float(precision=2),nullable=False)
    prestige = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(140))
    recorded_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Float(precision=2),default=0.0)
    def __repr__(self):
        return '<Trip {}>'.format(self.description)