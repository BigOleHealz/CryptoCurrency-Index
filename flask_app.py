from flask import Flask, render_template, url_for, flash, redirect, session, g
from forms import RegistrationForm, LoginForm
from big_ol_db import BigOlDB
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View, Link, Separator, Text
from datetime import datetime
import pymysql, hashlib, pandas as pd, logging, static.flash_messages as fl_mes
import random

app = Flask(__name__)

nav = Nav(app)

nav.register_element('my_navbar', Navbar('thenav',
	View('Home Page', 'index'),
	View('Item One', 'item', item=1),
	Link('Google', 'https://www.google.com'),
	Separator(),
	Text('Here is some Text'),
	Subgroup('Extras',
		Link('yahoo', 'https://www.yahoo.com'),
		View('Index', 'index'))
		))


app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

bodb = BigOlDB()




@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='about')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/items/<item>')
def item(item):
	return '<h1>THE ITEM PAGE!!! THE ITEM IS: {}.'.format(item)

# @app.before_request
# def before_request():
# 	g.user = None
# 	if "user" in session:
# 		g.user = session["user"]



# @app.route("/", methods=["GET", "POST"])
# def index():
# 	if request.method == "POST":
# 		session.pop("user", None)
# 		if request.form["password"] == "password":
# 			session['user'] = request.form["username"]
# 			return redirect(url_for("protected"))
# 	return render_template('index.html')

# @app.route("/protected")
# def protected():
# 	return render_template("protected.html")

# @app.route("/getsession")
# def get_session():
# 	if "user" in session:
# 		return session['user']
# 	return "Not logged in!"

# @app.route("/dropsession")
# def drop_session():
# 	session.pop("user", None)
# 	return "Dropped!"














@app.route("/register", methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		existing_account = bodb.existing_account(form.email.data, form.username.data)
		if existing_account == False:
			registered_status = bodb.register_user(form.email.data, form.username.data,
				form.password.data, form.first_name.data, form.last_name.data)

			if registered_status == True:
				flash(fl_mes.account_created.format(form.username.data), 'success')
			else:
				flash(registered_status, 'danger')

		else:
			flash(existing_account, 'danger')

		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		validated = bodb.validate_user(form.email.data, form.password.data)
		

		if validated == True:
			return redirect(url_for('home'))
		else:
			flash(validated, 'danger')
	return render_template('login.html', title='Login', form=form)


if __name__ == "__main__":
	app.run(debug=True)

