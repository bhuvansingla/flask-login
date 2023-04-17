from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField,TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from models import User

CHOICES = [('5', """Il giro che stai registrando è una gara ufficiale o un evento ufficiale di Team (con locandina)?"""),
           ('4', """Il giro che stai registrando è un'uscita non ufficiale di team nel weekend o festivi?"""),
           ('3', """Il giro che stai registrando è un'uscita infrasettimanale?""")]

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class NewTripForm(FlaskForm):
    tripname = StringField('Trip name',validators=[DataRequired()])
    speed = StringField('Average speed [km/h]',validators=[DataRequired()])
    distance = StringField('Distance [km]',validators=[DataRequired()])
    elevation = StringField('Elevation [m]',validators=[DataRequired()])
    prestige = RadioField('Choose an option', choices=CHOICES, validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add trip')

