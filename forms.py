from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField,RadioField,TextAreaField,FloatField,IntegerField,SelectField,FieldList
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange,Length, Regexp
from wtforms.widgets import FileInput

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
    speed = FloatField('Velocità media [km/h]',validators=[DataRequired()])
    distance = FloatField('Distanza [km]',validators=[DataRequired()])
    team = SelectField('Team', choices=[],coerce=int)
    elevation = FloatField('Dislivello [m]',validators=[DataRequired()])
    prestige = RadioField("Scegli un'opzione", choices=CHOICES, validators=[DataRequired()])
    n_of_partecipants = IntegerField('Numero di partecipanti del team (te incluso)', validators=[DataRequired(),NumberRange(min=1)])
    description = TextAreaField('Descrizione')
    is_approved = BooleanField("Approva")
    n_of_placements = IntegerField('Numero di piazzamenti',validators=[NumberRange(min=0)],default=0)

    submit = SubmitField('Aggiungi giro')
    submit_save = SubmitField('Salva')



class NewTeamForm(FlaskForm):
    name = StringField('Nome della squadra',validators=[DataRequired()])
    description = TextAreaField('Descrizione')
    submit = SubmitField('Aggiungi squadra')

class TeamProfileForm(FlaskForm):
    name = StringField('Nome della squadra',validators=[DataRequired()])
    description = TextAreaField('Descrizione')
    team_picture = FileField('')
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
    submit = SubmitField('Salva')