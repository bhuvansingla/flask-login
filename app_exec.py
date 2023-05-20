import base64
from app import app, login_manager
from routes import routes_general_scope,routes_team_area,routes_user_area,routes_admin_area
from models import User

@login_manager.user_loader
def load_user(id):
    
    return User.query.get(int(id))
  
@app.template_filter('b64encode')
def b64encode_filter(s):
    return base64.b64encode(s).decode('utf-8')

if __name__=="__main__":
    app.run(debug=True)