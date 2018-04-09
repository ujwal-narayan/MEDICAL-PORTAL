

from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
	""" Create user table"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))
	
	def __init__(self, username, password):
		self.username = username
		self.password = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())
	
	def validate_password(self, password):
		return bcrypt.verify(password, self.password)
	def __repr__(self):return "<User(username ='%s', password='%s')>" % (self.username, self.password)




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
		try :
			data = User.query.filter_by(username=name).first()
			if data is not None:
				if bcrypt.checkpw(passw.encode('utf8'), data.password.encode('utf8')) :
					session['logged_in'] = True
					return redirect(url_for('home'))
				else:
					return "Incorrect password"
			else:
				return 'Dont Login'
		except :
			return "User not found "

@app.route('/register/', methods=['GET', 'POST'])
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
		return "Error.Username unavailable"
	return render_template('register.html')

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.debug = True
	db.create_all()
	app.secret_key = "123"
	app.run()
	
