from app import app, db
from flask import request, render_template, flash, redirect,url_for
from flask_login import current_user, login_user, logout_user,login_required

from models import *
from forms import *

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
            next_page = url_for('user_home',username = user.username)
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
                    prestige = int(form.prestige.data),description=form.description.data,user_id=current_user.id,n_of_partecipants=form.n_of_partecipants.data)
       
        trip.score = Trip.calculate_score(trip.speed,trip.distance,trip.elevation,trip.prestige,trip.n_of_partecipants,[])
        db.session.add(trip)
        db.session.commit()
        flash('New trip registered!')
        return redirect(url_for('user_home',username = current_user.username))

    return render_template('new_trip.html',title="Add new trip", form = form )

@app.route('/user_home/<username>',methods=['GET', 'POST'])
@login_required
def user_home(username):
    
    user = User.query.filter_by(username=current_user.username).first()
    trips = Trip.query.filter_by(user_id=current_user.id)
    teams = Team.query.all()
    if trips is None:
        trips = []
    if teams is None:
        teams = []

    return render_template('user_home.html', user=user,trips=trips,teams=teams)



@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = User.query.get(current_user.id)
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user_profile'))
    return render_template('user_profile.html', form=form)

@app.route('/')
def index():

    return render_template('landing_page.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/delete_trip/<int:trip_id>")
def delete_trip(trip_id):
    trip = Trip.query.filter_by(id=trip_id).first()
    db.session.delete(trip)
    db.session.commit()
    return redirect(url_for("user_home",username=current_user.username))

@app.route("/delete_team/<int:team_id>")
def delete_team(team_id):
    team = Team.query.filter_by(id=team_id).first()
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for("user_home",username=current_user.username))


@app.route("/trip_details/<int:trip_id>")
def trip_details(trip_id):
    trip = Trip.query.get(trip_id)
    return render_template("trip_details.html",trip=trip)


@app.route("/team_details/<int:team_id>")
def team_details(team_id):
    team = Team.query.get(team_id)
    users_by_team = team.users
    ranking_list = []
    for user_by_team in users_by_team:
        all_scores_by_user = Trip.query.filter_by(user_id=user_by_team.id).all()
        tot_score_by_user =sum([score_by_user.score for score_by_user in all_scores_by_user])
        ranking_list.append({"user":user_by_team.username,"total score":tot_score_by_user})
    ranking_list = list(enumerate(sorted(ranking_list, key=lambda x: x['total score'],reverse=True)))
        
    return render_template("team_details.html",ranking_list=ranking_list,team=team)

@app.route('/new_team',methods=['GET', 'POST'])
@login_required
def new_team():
    if not current_user.is_admin:
        return 'Unauthorized'

    form = NewTeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data,description=form.description.data)
       
        db.session.add(team)
        db.session.commit()
        flash('New team registered!')
        return redirect(url_for('user_home',username = current_user.username))

    return render_template('new_team.html',title="Add new team", form = form )



@app.route('/admin_page',methods=['GET', 'POST'])
@login_required
def admin_page():
    
    if not current_user.is_admin:
        return 'Unauthorized'
    return render_template('admin_page.html',title="Admin page")

@app.route('/enroll_to_team/<int:team_id>',methods=['GET', 'POST'])
@login_required
def enroll_to_team(team_id):
    
    team = Team.query.get(team_id)
    if current_user not in team.users:
        team.add_member(current_user)
        db.session.commit()

    return redirect(url_for("user_home",username=current_user.username))

@app.route('/unenroll_from_team/<int:team_id>',methods=['GET', 'POST'])
@login_required
def unenroll_from_team(team_id):
    
    team = Team.query.get(team_id)

    if current_user in team.users:
        team.users.remove(current_user)
        db.session.commit()
    return redirect(url_for("user_home",username=current_user.username))
