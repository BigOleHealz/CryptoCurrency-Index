from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm
from big_ol_db import BigOlDB
import pymysql, hashlib, pandas as pd, logging, static.flash_messages as fl_mes

import graph_functions as gf
import numpy as np, json, plotly
import plotly.graph_objs as go


app = Flask(__name__)


app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

bodb = BigOlDB()


@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')

@app.route("/about")
def about():
	return render_template('about.html', title='about')






@app.route('/dashboard')
def index():
	feature = 'Notbar'
	
	ticker='BTC'
	figure = gf.create_plot(feature, ticker)

	return render_template('dashboard.html', plot=figure['data'], layout=figure['layout'])



@app.route('/bar', methods=['GET', 'POST'])
def change_features():
	ticker='BTC'
	feature = request.args['selected']
	graphJSON= gf.create_plot(feature, ticker)

	return graphJSON






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
	app.run(debug=True, port=8050)

