from datetime import datetime
from sqlalchemy import Integer,Column,String,DateTime,Float,Boolean,ForeignKey, BLOB
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class TeamUserAssociation(db.Model):
    __tablename__ = 'team_user_association'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    team_id = Column(Integer, ForeignKey('team.id', ondelete='CASCADE'))
    role =Column(String)
    join_date = Column(DateTime)


class AdminMixin:
    @property
    def is_admin(self):
        return self._is_admin == True

class User(db.Model,UserMixin,AdminMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(140))
    name = Column(String(140))
    surname = Column(String(140))
    email = Column(String(140))
    strava_account = Column(String(140))
    password = Column(String(140))
    password_hash = Column(String(140))
    phone_number = Column(String(140))
    trips = relationship('Trip',backref='user',lazy='dynamic',cascade="all, delete-orphan")
    teams = relationship('Team', secondary="team_user_association", back_populates='users')
    join_requests = relationship("RequestsToJoinTeam", back_populates="user", cascade="all, delete-orphan")
    profile_picture = Column(BLOB)
    _is_admin = Column(Boolean,nullable=True)

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
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"))
    team_id = Column(Integer, ForeignKey('team.id', ondelete="CASCADE"))
    score = Column(Integer,default=0)
    is_approved = Column(Boolean,default=False)

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
    trips = relationship('Trip',backref='team',lazy='dynamic',cascade="all, delete-orphan")
    users = relationship('User', secondary="team_user_association", back_populates='teams')
    join_requests = relationship("RequestsToJoinTeam", back_populates="team", cascade="all, delete-orphan")
    description = Column(String(140))
    
    def __repr__(self):
        return '<Team {}>'.format(self.description)

    def add_member(self, member:User,role:str,join_date:datetime = None):
        t_u_association = TeamUserAssociation(team_id=self.id,user_id=member.id,role=role,join_date=join_date)
        db.session.add(t_u_association)
        db.session.commit()


class RequestsToJoinTeam(db.Model):
    __tablename__ = 'requests_to_join_team'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    team_id = Column(Integer, ForeignKey('team.id', ondelete='CASCADE'))
    status = Column(String)
    request_date = Column(DateTime)

    user = relationship("User", back_populates="join_requests")
    team = relationship("Team", back_populates="join_requests")


