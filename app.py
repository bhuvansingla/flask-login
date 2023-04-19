from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__,template_folder="templates")


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
app.secret_key = os.urandom(24)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

from routes import *
from models import User

@login_manager.user_loader
def load_user(id):
    
    return User.query.get(int(id))
  

if __name__=="__main__":
    with app.app_context():

        db.create_all()
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin",role="admin")
            admin.set_password("admin")

            db.session.add(admin)
            db.session.commit()
        app.run(debug=True)