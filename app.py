from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from datetime import timedelta
import base64

app = Flask(__name__,template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://waltpianist97:LaBombaDB23@waltpianist97.mysql.pythonanywhere-services.com/waltpianist97$la_bomba_db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.secret_key = os.urandom(24)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
