from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField,RadioField,TextAreaField,FloatField,IntegerField,SelectField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange,Length, Regexp
from wtforms.widgets import FileInput

from datetime import date




CHOICES = [(5, """Il giro che stai registrando è una gara ufficiale o un evento ufficiale di Team (con locandina)?"""),
           (4, """Il giro che stai registrando è un'uscita non ufficiale di team nel weekend o festivi?"""),
           (3, """Il giro che stai registrando è un'uscita infrasettimanale?""")]

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', \
                                                                                            message='La password deve contenere almeno 8 caratteri, di cui almeno\
                                                                                            una lettera maiuscola, una minuscola, una cifra ed un carattere speciale (@$!%*?&)')])

    password2 = PasswordField(
        'Ripeti Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrati')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Invia email')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', \
                                                                                            message='La password deve contenere almeno 8 caratteri, di cui almeno\
                                                                                            una lettera maiuscola, una minuscola, una cifra ed un carattere speciale (@$!%*?&)')])
    password2 = PasswordField(
        'Ripeti Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset password')

class NewTripForm(FlaskForm):
    tripname = StringField('Nome del giro',validators=[DataRequired()])
    speed = FloatField('Velocità media [km/h]',validators=[DataRequired()], render_kw={'placeholder': '1000.00'})
    distance = FloatField('Distanza [km]',validators=[DataRequired()], render_kw={'placeholder': '1000.00'})
    team = SelectField('Team', choices=[],coerce=int)
    elevation = FloatField('Dislivello [m]',validators=[DataRequired()],render_kw={'placeholder': '1000.00'})
    recorded_on = StringField('Seleziona la data del giro', render_kw={'placeholder': 'dd/mm/yyyy'})
    prestige = RadioField("Scegli un'opzione per il prestigio", choices=CHOICES, validators=[DataRequired()])
    n_of_partecipants = IntegerField('Numero di partecipanti del team (te incluso)', validators=[DataRequired(),NumberRange(min=1)])
    description = TextAreaField('Descrizione')
    is_approved = BooleanField("Approva")
    n_of_placements = IntegerField('Piazzamenti',validators=[NumberRange(min=0)],default=0)
    submit = SubmitField('Aggiungi giro')
    submit_save = SubmitField('Salva')



class NewTeamForm(FlaskForm):
    name = StringField('Nome della squadra',validators=[DataRequired()])
    description = TextAreaField('Descrizione')
    submit = SubmitField('Aggiungi squadra')

class TeamProfileForm(FlaskForm):
    name = StringField('Nome della squadra',validators=[DataRequired()])
    description = TextAreaField('Descrizione')
    team_picture = FileField('Immagine del team')
    team_background = FileField('Background del team')
    team_banner = FileField('Banner del team')
    team_motto = FileField('Motto del team')
    submit = SubmitField('Salva')


class CustomFileInput(FileInput):
    def __call__(self, field, **kwargs):
        if field.data:
            kwargs['value'] = field.filename
        return super().__call__(field, **kwargs)
    
class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name =  StringField('Nome', validators=[DataRequired()])
    surname = StringField('Cognome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    strava_account = StringField('Account di strava')
    phone_number = StringField("Numero di telefono")
    profile_picture = FileField('Immagine di profilo')
    profile_background = FileField('Background di profilo')
    profile_banner = FileField('Banner di profilo')
    submit = SubmitField('Salva')