

from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bcrypt
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)
migrate = Migrate(app, db)




class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    dayavail = db.Column(db.String(128))
    starttime = db.Column(db.String(80))
    endtime = db.Column(db.String(80))

    def __init__(self, username, password, dayavail, starttime, endtime):
        self.username = username
        self.password = bcrypt.hashpw(
            password.encode('utf8'), bcrypt.gensalt())
        self.dayavail = dayavail
        self.starttime = starttime
        self.endtime = endtime

    def validate_password(self, password):
        return bcrypt.verify(password, self.password)

    def __repr__(self): return "<User(username ='%s', password='%s',\
    dayavail='%s', starttime='%s', endtime='%s',)>" % (
        self.username, self.password, self.dayavail, self.starttime, self.endtime)


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            return render_template('index.html')
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        try:
            data = User.query.filter_by(username=name).first()
            print(data)
            if data is not None:
                if bcrypt.checkpw(passw.encode('utf8'),
                                  data.password):
                    session['logged_in'] = True
                    return redirect(url_for('home'))
                else:

                    error = "Incorrect password.Please Try Again."
                    # return redirect(url_for('login'))
                    return render_template('login.html', error=error)

            else:
                error = 'User was not found. Please register \
                before trying again'
                # return redirect(url_for('login'))
                return render_template('login.html', error=error)

        except Exception as e:
            print(str(e))
            error = "An Error was encountered please try again"
            # return redirect(url_for('login'))
            return render_template('login.html', error=error)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        try:
            new_user = User(
                username=request.form['username'],
                password=request.form['password'],
                dayavail='None',
                starttime='None',
                endtime='None')
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
        except Exception as e:
            print(str(e))
            error = "Error.Username unavailable.Please try again \
            with a different username"
            return render_template('register.html', error=error)
    return render_template('register.html')

@app.route('/register_doctor/', methods=['GET', 'POST'])
def register_doctor():
    """Register Form"""
    days = ['Weekdays', 'Sat', 'Sun', 'Mon-Thu']
    if request.method == 'GET':
        return render_template('register_doctor.html', days=days)
    elif request.method == 'POST':
        try:
            day_avail_list=request.form.getlist('docavail')
            avails = ",".join(day_avail_list)
            new_user = User(
                username=request.form['username'],
                password=request.form['password'],
                dayavail=avails,
                starttime=request.form['timestart'],
                endtime=request.form['timeend'])
                
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
        except Exception as e:
            print(str(e))
            error = "Error.Username unavailable.Please try again \
            with a different username"
            return render_template('register_doctor.html', error=error, days=days)
    return render_template('register_doctor.html',days=days)


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))


@app.route("/finddoctor")
def finddoctor():
    return render_template('finddoctor.html')


@app.route("/bookapt", methods=['GET', 'POST'])
def bookapt():
    if request.method == 'GET':
        docs = ['Doctor1', 'Doctor2', 'Doctor3']
        return render_template('bookapt.html',  docs=docs)
        # return render_template('bookapt.html')
    else:
        aptdate = request.form['aptdate']
        apttime = request.form['apttime']
        aptdoc = request.form['aptdoc']


if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run()
