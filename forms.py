from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField,RadioField,TextAreaField,FloatField,IntegerField,SelectField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange,Length, Regexp

CHOICES = [(5, """Il giro che stai registrando è una gara ufficiale o un evento ufficiale di Team (con locandina)?"""),
           (4, """Il giro che stai registrando è un'uscita non ufficiale di team nel weekend o festivi?"""),
           (3, """Il giro che stai registrando è un'uscita infrasettimanale?""")]

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', \
                                                                                            message='Password must be at least 8 characters long and contain at least \
                                                                                            one lowercase letter, one uppercase letter, one digit, and one special character (@$!%*?&)')])

    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send email')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', \
                                                                                            message='Password must be at least 8 characters long and contain at least \
                                                                                            one lowercase letter, one uppercase letter, one digit, and one special character (@$!%*?&)')])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset password')

class NewTripForm(FlaskForm):
    tripname = StringField('Trip name',validators=[DataRequired()])
    speed = FloatField('Average speed [km/h]',validators=[DataRequired()])
    distance = FloatField('Distance [km]',validators=[DataRequired()])
    team = SelectField('Team choice', choices=[],coerce=int)
    elevation = FloatField('Elevation [m]',validators=[DataRequired()])
    prestige = RadioField('Choose an option', choices=CHOICES, validators=[DataRequired()])
    n_of_partecipants = IntegerField('Number of partecipants', validators=[DataRequired(),NumberRange(min=1)])
    description = TextAreaField('Description')
    is_approved = BooleanField("Approve")
    submit = SubmitField('Add trip')
    submit_save = SubmitField('Save')


class NewTeamForm(FlaskForm):
    name = StringField('Team name',validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Team')

from wtforms.widgets import FileInput

class CustomFileInput(FileInput):
    def __call__(self, field, **kwargs):
        if field.data:
            kwargs['value'] = field.filename
        return super().__call__(field, **kwargs)
    
class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name =  StringField('First Name', validators=[DataRequired()])
    surname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    strava_account = StringField('Strava account')
    phone_number = StringField("Phone number")
    profile_picture = FileField('')
    submit = SubmitField('Save')