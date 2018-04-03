from app import app
from flask import render_template
@app.route('/')
@app.route('/index')
def index():
	user = { 'username':'Ujwal' }
	posts = [ {
	'author' : {'username':'Sravani'},
	'body' : 'Ujwal is the bestest'
	},
	{
	'author' : { 'username':'Shivang'},
	'body' : 'Best ITWS ta ever '
	}]

	return render_template('index.html',title='Home', user=user,posts=posts)
