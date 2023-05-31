from app import app, db
from flask import request, render_template, flash, redirect,url_for, send_from_directory
from flask_login import current_user, login_user, logout_user,login_required
from sqlalchemy import or_, and_, desc, func
from models import User, Trip, Team, TeamUserAssociation, RequestsToJoinTeam, PlacementsInTrip
from forms import *
from werkzeug.urls import url_parse
import secrets
from datetime import datetime, timedelta
import smtplib
from tools import AUTO_MAIL, send_email_utility
DATE_FORMAT = "%d/%m/%Y"

#%% GENERAL   
with app.app_context():

    db.create_all()
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin",_is_admin=True)
        admin.set_password("admin")
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if not current_user.is_anonymous:
        return redirect(url_for('user_home',username=current_user.username))

    return render_template('landing_page.html')


@app.route('/new_trip/<int:user_id>', methods=['GET', 'POST'])
@app.route('/new_trip/<int:user_id>/<int:team_id>', methods=['GET', 'POST'])
@login_required
def new_trip(user_id,team_id=None):
    form = NewTripForm()
    user = User.query.get(user_id)

    if not team_id:
        if user == current_user:
            form.team.choices = [(team.id, team.name) for team in user.teams]
        else:
            form.team.choices = [(team.id, team.name) for team in user.teams if current_user in team.users]
    else:
        team_chosen = Team.query.get(team_id)
        form.team.choices = [(team_chosen.id,team_chosen.name)]
        form.team.data = team_chosen.id
        form.team.render_kw = {'disabled': 'disabled'}


    if request.method=="POST":

        try:
            recorded_on =  datetime.strptime(form.recorded_on.data,DATE_FORMAT)
        except ValueError:
            # Invalid date format
            return render_template('new_trip.html',title="Add new trip", form = form )

        trip = Trip(tripname=form.tripname.data,speed=form.speed.data, n_of_placements=form.n_of_placements.data,
                    distance=form.distance.data,elevation=form.elevation.data, team_id=form.team.data, recorded_on=recorded_on,
                    prestige = int(form.prestige.data),description=form.description.data,user_id=user_id,n_of_partecipants=form.n_of_partecipants.data)
        
        placement_values=[]
        for i in range(form.n_of_placements.data):
            field_name = f"placement-{i}"
            placement_value = request.form.get(field_name)
            placement_values.append(int(placement_value))
       

        t_r = TeamUserAssociation.query.filter(and_(TeamUserAssociation.user_id==user.id,TeamUserAssociation.team_id==form.team.data)).first().role

        if t_r == "team_leader" or user._is_admin: 
            trip.is_approved = True
            trip.score = Trip.calculate_score(trip.speed,trip.distance,trip.elevation,trip.prestige,trip.n_of_partecipants,placement_values)
        else:
            trip.is_approved = False

        db.session.add(trip)
        db.session.commit()
        flash('New trip registered!')

        for placement_value in placement_values:
            placement = PlacementsInTrip(trip_id=trip.id, place=placement_value)
            db.session.add(placement)
        db.session.commit()

        if t_r!="team_leader":
            team=Team.query.get(trip.team_id)
            emails_leaders = [tl.email for tl in team.get_leaders()]
            send_email_utility('Richiesta approvazione giro',f"{user.username} ha richiesto di registrare il giro: {trip.tripname}, controlla la tua pagina 'Gestisci giri'!",AUTO_MAIL,emails_leaders)

        if user == current_user:
            return redirect(url_for('trips_overview',user_id=user.id))
        else:
            return redirect(url_for('member_view',team_id=form.team.data,user_id=user.id))

    return render_template('new_trip.html',title="Add new trip", form = form )

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route("/edit_trip/<int:trip_id>/<int:user_id>", methods=['GET', 'POST'])
@login_required
def edit_trip(trip_id,user_id):
    trip = Trip.query.get(trip_id)
    placements = trip.get_placements()
    user = User.query.get(user_id)
    my_role_in_team = user.get_role_in_team(trip.team_id)
    form = NewTripForm(obj=trip)
    trip_team = Team.query.get(trip.team_id)
    form.team.choices = [(trip_team.id,trip_team.name)]
    form.team.render_kw = {'disabled': 'disabled'}

    form.recorded_on.data = trip.recorded_on.strftime(DATE_FORMAT)


    if request.method == 'POST':

        [db.session.delete(placement) for placement in placements]
        db.session.commit()

        trip.tripname = request.form["tripname"]
        trip.speed = float(request.form["speed"])
        trip.distance = float(request.form["distance"])
        trip.elevation = float(request.form["elevation"])
        trip.prestige = int(request.form["prestige"])
        trip.description = request.form["description"]
        trip.user_id = user_id
        trip.n_of_partecipants = int(request.form["n_of_partecipants"])
        placement_values = [int(pl) for pl in request.form.getlist('placement[]')]
        edit_placements = [int(pl) for pl in request.form.getlist('edit_placement')]
        placement_ids  = request.form.getlist('placement_id')
     

        try:
            trip.recorded_on =  datetime.strptime(request.form["recorded_on"],DATE_FORMAT)
        except ValueError:
            # Invalid date format
            return render_template('edit_trip.html', form=form,trip_id=trip.id,user_id=user_id,my_role_in_team=my_role_in_team,is_approved=trip.is_approved,placements=placements)

        if edit_placements:
            for id, place in zip(placement_ids, edit_placements):
                placement = PlacementsInTrip(id=id, trip_id=trip.id, place=int(place))
                db.session.add(placement)
                
        for placement_value in placement_values:
            placement = PlacementsInTrip(trip_id=trip.id, place=int(placement_value))
            db.session.add(placement)

        db.session.commit() 

        if trip.is_approved:
            placements_updated = [pl.place for pl in trip.get_placements()]
            trip.score = Trip.calculate_score(trip.speed,trip.distance,trip.elevation,trip.prestige,trip.n_of_partecipants,placements_updated)
        else:
            trip.score = 0
        db.session.commit()
        flash('Your trip has been updated!', 'success')

       
        if user != current_user:
            if trip.is_approved:
                return redirect(url_for('member_view',team_id=trip.team_id,user_id=trip.user_id))
            else:
                return redirect(url_for('manage_trips',team_id=trip.team_id))
        else:
            return redirect(url_for('trips_overview',user_id=user.id))

 

    return render_template('edit_trip.html', form=form,trip_id=trip.id,user_id=user_id,my_role_in_team=my_role_in_team,is_approved=trip.is_approved,placements=placements)

@app.route("/delete_trip/<int:trip_id>/<int:user_id>")
@login_required
def delete_trip(trip_id,user_id):
    trip = Trip.query.filter_by(id=trip_id).first()
    db.session.delete(trip)
    db.session.commit()
    if user_id == current_user.id:
        return redirect(url_for('trips_overview',user_id=current_user.id))
    else:
        return redirect(url_for('member_view', user_id=user_id,team_id=trip.team_id))
  


#%% LOGIN SECTION
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
            if not user._is_admin:
                next_page = url_for('user_home',username = user.username)
            else:
                next_page = url_for('admin_home')
            
        return redirect(next_page)

                 
    return render_template('login.html', title='Sign In', form=form)

# Temporary storage for password reset requests
password_reset_requests = {}
# Form for password reset request
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        user_recover = User.query.filter_by(username=username).first()
        if not user_recover:
            flash(f"There is no \'{username}\' registered in the system!")
            return redirect(url_for('login'))

        email = user_recover.email
        # Generate a unique token
        token = secrets.token_hex(16)
        # Store the token in the temporary database
        password_reset_requests[token] = {'email': email, 'timestamp': datetime.now()}
        # Send an email to the user with the password reset link
        # You'll need to replace the placeholders with your own values
        send_email_utility('Password reset', f'Clicca il seguente link per resettare la tua password: {url_for("reset_password", token=token, _external=True)}',AUTO_MAIL,email)
              
        flash('An email has been sent to your account with further instructions.')
        return redirect(url_for('login'))
    
# Form for resetting the password
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Check if the token is valid and hasn't expired
    if token not in password_reset_requests:
        flash(f'The token is invalid!')
        return redirect(url_for('login'))

    request_data = password_reset_requests[token]
    print(request_data)
    if datetime.now() - request_data['timestamp'] > timedelta(minutes=5):
        # Expired token
        del password_reset_requests[token]
        flash(f'Token has expired. Retry a new password reset request!')
        return redirect(url_for('login'))
   
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Update the user's password in the database 
        user_changing_pwd =User.query.filter_by(email=request_data['email']).first()
        # You'll need to replace this with your own code to update the user's password
        user_changing_pwd.set_password(form.password.data)
        db.session.commit()
        # Delete the token from the temporary database
        del password_reset_requests[token]
        flash(f'Password reset succesful!')
        return redirect(url_for('login'))

    return render_template('reset_password.html',form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
  #check if current_user logged in, if so redirect to a page that makes sense
    if current_user.is_authenticated and not current_user._is_admin:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user_check = User.query.filter(or_(User.email==form.email.data, User.username==form.username.data)).first()
        if user_check:
            if user_check.email == form.email.data:
                flash('The email already exist, please register under different email!')
            if user_check.username == form.username.data:
                flash('The username already exist, please register under different username!')

            return redirect(url_for('register'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
   
        
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
