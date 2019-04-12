from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm
from big_ol_db import BigOlDB
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View, Link, Separator, Text
from datetime import datetime
import pymysql, hashlib, pandas as pd, logging, static.flash_messages as fl_mes

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






@app.route('/index')
def index():
    feature = 'Bar'
    bar = create_plot(feature)
    return render_template('index.html', plot=bar)

def create_plot(feature):
    if feature == 'Bar':
        N = 40
        x = np.linspace(0, 1, N)
        y = np.random.randn(N)
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
        data = [
            go.Bar(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/bar', methods=['GET', 'POST'])
def change_features():

    feature = request.args['selected']
    graphJSON= create_plot(feature)

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

