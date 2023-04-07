from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    #add phone number
    phone = db.Column(db.String(100))
    #add email
    email = db.Column(db.String(100))
    #add address
    address = db.Column(db.String(100))

    def __init__(self, username, password, phone, email, address):
        self.username = username
        self.password = password
        self.phone = phone
        self.email = email
        self.address = address


@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
            
        # open the home page and display the user's name
        return render_template('home.html', name=session.get("username"))
        #return render_template('home.html')
    else:
        return render_template('index.html', message="Hello!")


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password'],phone=request.form['phone'],email=request.form['email'],address=request.form['address']))

            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        data = User.query.filter_by(username=username, password=password).first()
        if data is not None:
            session['logged_in'] = True
            session['username'] = username
            session['email'] = data.email
            session['phone'] = data.phone
            session['address'] = data.address
            

            return redirect(url_for('index'))
        return render_template('index.html', message="Incorrect Details")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/modify', methods=['GET', 'POST'])
def modify():
    session['logged_in'] = False
    print(request.form['phone'])
    data = User.query.filter_by(username=session['username']).first()
    """
    if request.form['phone'] != "":
        data.phone = request.form['phone']
    if request.form['email'] != "":
        data.email = request.form['email']
    if request.form['address'] != "":
        data.address = request.form['address']
    #display success message 

    db.session.commit()
    """
    return redirect(url_for('index'))

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    session['logged_in'] = False
    data = User.query.filter_by(username=session['username']).first()
    db.session.delete(data)
    db.session.commit()


    return redirect(url_for('index'))




if(__name__ == '__main__'):
    app.secret_key = "ThisIsNotASecret:p"
    with app.app_context():
        db.create_all()
        app.run()
