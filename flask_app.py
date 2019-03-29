from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from big_ol_db import BigOlDB
from datetime import datetime
import pymysql, hashlib, pandas as pd, logging, static.flash_messages as fl_mes

app = Flask(__name__)

app.config['SECRET_KEY'] = '8b0f39878e8d95081dff1bb8e35b526a'

bodb = BigOlDB()


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='about')


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

