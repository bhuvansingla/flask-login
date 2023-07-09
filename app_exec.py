from app import app, login_manager
from routes import routes_general_scope,routes_team_area,routes_user_area,routes_admin_area
from models import User

@login_manager.user_loader
def load_user(id):
    
    return User.query.get(int(id))
  

if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
