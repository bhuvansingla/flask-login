from app import app, db
from flask import request, render_template, flash, redirect,url_for
from flask_login import current_user, login_user, logout_user,login_required
from sqlalchemy import or_, and_, desc, func
from models import User, Trip, Team, TeamUserAssociation, RequestsToJoinTeam
from forms import *
from werkzeug.urls import url_parse
import secrets
from datetime import datetime, timedelta
from tools import send_email_utility, AUTO_MAIL


@app.route("/team_profile/<int:team_id>", methods=['GET', 'POST'])
@login_required
def team_profile(team_id):

    team = Team.query.get(team_id)
    my_role_in_team = current_user.get_role_in_team(team_id=team_id)
    form = TeamProfileForm(obj=team)
    if form.validate_on_submit():
        # Handle profile picture upload
        team.name = form.name.data
        team.description = form.description.data

        if form.team_picture.data:
            team.team_picture = form.team_picture.data.read()

        if form.team_background.data:
            team.team_background = form.team_background.data.read()
        
        if form.team_banner.data:
            team.team_banner = form.team_banner.data.read()

        if form.team_motto.data:
            team.team_motto = form.team_motto.data.read()

        db.session.commit()
        flash('Your team has been updated!', 'success')
        return redirect(url_for('team_profile',team_id=team_id))
    
    # Disable the form fields
    if my_role_in_team!="team_leader":
        for field in form:
            field.render_kw = {'disabled': True}
    
    return render_template('team_profile.html', form=form,team=team,role=my_role_in_team)

@app.route('/manage_team/<int:team_id>',methods=['GET', 'POST'])
@login_required
def manage_team(team_id):

    team = Team.query.filter_by(id=team_id).first()
    team_members = [{"user": user, "role": user.get_role_in_team(team_id=team_id), "team_id":team_id} for user in team.users]
 
    requests_to_join = RequestsToJoinTeam.query.filter_by(team_id=team_id).all()
    requests_to_join = [{"id":request_to_join.id,"user":User.query.get(request_to_join.user_id)} for request_to_join in requests_to_join] 

    return render_template('manage_team.html',title="Manage team",team = team,team_members=team_members,requests_to_join=requests_to_join)


@app.route('/manage_trips/<int:team_id>',methods=['GET', 'POST'])
@login_required
def manage_trips(team_id):
    team = Team.query.get(team_id)
    trips = Trip.query.filter(Trip.team_id==team_id).all()
    approved_trips = [{"user":trip.get_user(),"trip":trip} for trip in trips if trip.is_approved]
    non_approved_trips = [{"user":trip.get_user(),"trip":trip} for trip in trips if not trip.is_approved]

    return render_template('manage_trips.html',title="Manage trips",approved_trips = approved_trips,non_approved_trips=non_approved_trips,team=team)

@app.route('/approve_trip/<int:trip_id>',methods=["GET","POST"])
@login_required
def approve_trip(trip_id):
    trip = Trip.query.get(trip_id)
    team = Team.query.get(trip.team_id)
    approved_member = User.query.get(trip.user_id)
    other_members_emails = [user.email for user in team.users]

    trip.is_approved=True
    
    db.session.commit()
   
    send_email_utility("Approvazione giro",f"Il tuo giro: {trip.tripname} e' stato approvato da {current_user.username}",AUTO_MAIL, approved_member.email)
    send_email_utility("Registrazione nuovo giro",f"Il giro: {trip.tripname} di {approved_member.username} e' stato registrato",AUTO_MAIL,other_members_emails)


    return redirect(url_for("manage_trips",team_id=team.id))
  

@app.route('/change_role/<int:team_id>/<int:user_id>',methods=['POST'])
@login_required
def change_role(team_id,user_id):
    team_name = Team.query.get(team_id).name
    user = User.query.get(user_id)
    role = request.form.get('role')
    user_role_in_team = user.get_role_in_team(team_id)
    if user_role_in_team != role:
        user.set_role_in_team(team_id,role)
        send_email_utility('Cambio di ruolo', f"Il tuo ruolo nel {team_name} e' stato cambiato da {user_role_in_team} a {role}!",AUTO_MAIL,user.email)

    db.session.commit()
   
    if current_user._is_admin:
        return redirect(url_for('view_user_profile_by_admin',user_id=user.id))
    else:
        return redirect(url_for('manage_team',team_id=team_id))

 
@app.route("/team_home/<int:team_id>")
@login_required
def team_home(team_id):
    team = Team.query.get(team_id)
    members_by_team = User.query.filter(User.id.in_([member.id for member in team.users])).all()
    ranking_list = []
    my_role_in_team = current_user.get_role_in_team(team_id=team_id)
    my_request_to_join_team = RequestsToJoinTeam.query.filter_by(team_id=team_id,user_id=current_user.id).first()
    for user_by_team in members_by_team:
        all_scores_by_user = Trip.query.filter_by(user_id=user_by_team.id,team_id=team_id,is_approved=True).all()
        tot_score_by_user =sum([score_by_user.score for score_by_user in all_scores_by_user])
        ranking_list.append({"user_id":user_by_team.id,"user":user_by_team.username,"total score":tot_score_by_user})
    ranking_list = list(enumerate(sorted(ranking_list, key=lambda x: x['total score'],reverse=True)))

    return render_template("team_home.html",ranking_list=ranking_list,team=team,user=current_user, role=my_role_in_team,request=my_request_to_join_team)


@app.route("/member_view/<int:user_id>/<int:team_id>")
@login_required
def member_view(user_id,team_id):
    member = User.query.get(user_id)
    team = Team.query.get(team_id)
    if current_user in team.users:
        my_role_in_team = TeamUserAssociation.query.filter(and_(TeamUserAssociation.user_id==current_user.id,TeamUserAssociation.team_id==team_id)).first().role
    else:
        my_role_in_team = None

    trips_in_team = Trip.query.filter(and_(Trip.user_id==user_id,Trip.team_id==team_id)).all()
    stat={}
    stat["average_speed"] = db.session.query(Trip, func.avg(Trip.speed)).group_by(Trip.user_id).filter_by(user_id=member.id,team_id=team.id).all()
    if stat["average_speed"]:
        stat["average_speed"] = round(stat["average_speed"][0][1],2)
    stat["maximum_elevation"] = db.session.query(Trip, func.max(Trip.elevation)).group_by(Trip.user_id).filter_by(user_id=member.id,team_id=team.id).all()
    if stat["maximum_elevation"]:
        stat["maximum_elevation"]= stat["maximum_elevation"][0][1]
    stat["total_distance"] = db.session.query(Trip, func.sum(Trip.distance)).group_by(Trip.user_id).filter_by(user_id=member.id,team_id=team.id).all()
    if stat["total_distance"]:
        stat["total_distance"]= round(stat["total_distance"][0][1],2)
    stat["activities"] = len(Trip.query.filter_by(user_id=member.id,team_id=team.id).all())

    return render_template("member_view.html",trips= trips_in_team,user=member,team=team, role=my_role_in_team,stat=stat)

@app.route('/member_profile/<int:user_id>/<int:team_id>', methods=['GET', 'POST'])
@login_required
def member_profile(user_id,team_id):
    user = User.query.get(user_id)
    team = Team.query.get(team_id)
    return render_template('member_profile.html',team=team,user=user)

@app.route('/non_member_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def non_member_profile(user_id):
    user = User.query.get(user_id)
    return render_template('non_member_profile.html',user=user)


@app.route("/non_member_view/<int:user_id>")
@login_required
def non_member_view(user_id):
    non_member = User.query.get(user_id)
    last_trips = Trip.query.order_by(desc(Trip.recorded_on)).filter_by(user_id = user_id).limit(3).all()
    if last_trips is None:
        last_trips = []

    stat={}
    stat["average_speed"] = db.session.query(Trip, func.avg(Trip.speed)).group_by(Trip.user_id).filter_by(user_id=user_id).all()
    if stat["average_speed"]:
        stat["average_speed"] = round(stat["average_speed"][0][1],2)
    stat["maximum_elevation"] = db.session.query(Trip, func.max(Trip.elevation)).group_by(Trip.user_id).filter_by(user_id=user_id).all()
    if stat["maximum_elevation"]:
        stat["maximum_elevation"]= stat["maximum_elevation"][0][1]
    stat["total_distance"] = db.session.query(Trip, func.sum(Trip.distance)).group_by(Trip.user_id).filter_by(user_id=user_id).all()
    if stat["total_distance"]:
        stat["total_distance"]= round(stat["total_distance"][0][1],2)
    stat["activities"] = len(Trip.query.filter_by(user_id=user_id).all())

    return render_template('non_member_view.html', user=non_member, last_trips=last_trips,stat=stat)


@app.route('/decide_on_enrollment/<int:request_id>/<accept>',methods=['GET', 'POST'])
@login_required
def decide_on_enrollment(request_id,accept):
    
    request_to_join = RequestsToJoinTeam.query.get(request_id)
    user = User.query.get(request_to_join.user_id)
    team = Team.query.get(request_to_join.team_id)
   
    if accept=="Yes": 
        team.add_member(user,role="user")
        send_email_utility(f"La tua richiesta a {team.name}",f"La tua richiesta di unirti al team {team.name} e' stata approvata!",AUTO_MAIL,user.email)
    else:
        send_email_utility(f"La tua richiesta a {team.name}",f"La tua richiesta di unirti al team {team.name} e' stata rifiutata!",AUTO_MAIL,user.email)

    db.session.delete(request_to_join)
    db.session.commit()
    
    return redirect(url_for("manage_team",team_id = request_to_join.team_id))
