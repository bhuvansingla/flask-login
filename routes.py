from app import app, db
from flask import request, render_template, flash, redirect,url_for
from flask_login import current_user, login_user, logout_user,login_required

from models import User,Trip
from forms import RegistrationForm,LoginForm, NewTripForm

from werkzeug.urls import url_parse
import urllib

@app.route('/login', methods=['GET', 'POST'])
def login():
  #check if current_user logged in, if so redirect to a page that makes sense
    if current_user.is_authenticated:
        return redirect(url_for('index'))   
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user',username = user.username)
            return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
  #check if current_user logged in, if so redirect to a page that makes sense
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/new_trip',methods=['GET', 'POST'])
@login_required
def new_trip():
    
    form = NewTripForm()
    if form.validate_on_submit():
        trip = Trip(tripname=form.tripname.data,speed=form.speed.data,
                    distance=form.distance.data,elevation=form.elevation.data,
                    prestige = form.prestige.data,description=form.description.data,user_id=current_user.id)
        trip.score = 0.0
        db.session.add(trip)
        db.session.commit()
        flash('New trip registered!')
        return redirect(url_for('user',username = current_user.username))

    return render_template('new_trip.html',title="Add new trip", form = form )

@app.route('/user/<username>',methods=['GET', 'POST'])
@login_required
def user(username):
    
    user = User.query.filter_by(username=current_user.username).first()
    trips = Trip.query.filter_by(user_id=current_user.id)
    if trips is None:
        trips = []

    return render_template('user.html', user=user,trips=trips)


@app.route('/')
def index():
  
    return render_template('landing_page.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/delete/<int:trip_id>")
def delete(trip_id):
    trip = Trip.query.filter_by(id=trip_id).first()
    db.session.delete(trip)
    db.session.commit()
    return redirect(url_for("user",username=current_user.username))

@app.route("/trip_details/<int:trip_id>")
def trip_details(trip_id):
    trip = Trip.query.get(trip_id)
    return render_template("trip_details.html",trip=trip)