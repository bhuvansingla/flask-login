from datetime import datetime
from sqlalchemy import Table,Integer,Column,String,DateTime,Float,ForeignKey,func
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


team_user_association = Table('team_user_association', db.Model.metadata,
    Column('team_id', Integer, ForeignKey('team.id')),
    Column('user_id', Integer, ForeignKey('user.id'))
)


class AdminMixin:
    @property
    def is_admin(self):
        return self.role == 'admin'

class User(db.Model,UserMixin,AdminMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(140))
    email = db.Column(db.String(140))
    strava_account = db.Column(db.String(140))
    password = db.Column(db.String(140))
    password_hash = db.Column(db.String(140))
    phone_number = db.Column(db.String(140))
    trips = db.relationship('Trip',backref='user',lazy='dynamic')
    teams = relationship('Team', secondary=team_user_association, back_populates='users')
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Trip(db.Model):
    id = Column(Integer, primary_key=True)
    tripname = Column(String(140))
    speed = Column(Float(precision=2),nullable=False)
    distance = Column(Float(precision=2),nullable=False)
    elevation = Column(Float(precision=2),nullable=False)
    prestige = Column(Integer,nullable=False)
    description = Column(String(140))
    recorded_on = Column(DateTime, index=True, default=datetime.utcnow)
    n_of_partecipants = Column(Integer, nullable=False, default=1)
    placement = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    score = Column(Float(precision=2),default=0.0)
    
    def __repr__(self):
        return '<Trip {}>'.format(self.description)

    @staticmethod
    def calculate_score(v,dx,dz,pr,np,piazzamenti):
        """dx: distance in km,
        dz: the height in m,
        pr: the prestige, 
        np: the number of players, 
        v: the velocity in km/h
        piazzamenti: the list of top placements"""
        l=5e-3                              
        d=2.5e-4
        punteggio_finale_o = lambda v,dx,dz,pr: dx*l*(dz*d+0.25)*(0.7+0.15*(pr-3)) if v<=25.0 else dx*l*(dz*d+0.25)*(0.7+0.15*(pr-3))*(1+0.05*(v-25.0))
        punteggio_finale_f = lambda punteggio_finale_o,np,piazzamenti: int(round((punteggio_finale_o + (np-1)/10)*100,0))+11*len(piazzamenti)-sum(piazzamenti)

        p_f_o = punteggio_finale_o(v,dx,dz,pr)
        return punteggio_finale_f(p_f_o,np,piazzamenti)
        
class Team(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    users = relationship('User', secondary=team_user_association, back_populates='teams')
    description = Column(String(140))
    
    def __repr__(self):
        return '<Team {}>'.format(self.description)

    def add_member(self, member):
        self.users.append(member)