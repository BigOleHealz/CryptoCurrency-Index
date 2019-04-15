#!/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from styles import style_dicts as styles, value_dicts as vals
from aggregator_functions import AggregatorFunctions as agg
from big_ol_db import BigOlDB
from argparse import ArgumentParser


external_stylesheets = [dbc.themes.BOOTSTRAP, 
	'https://codepen.io/plotly/pen/YeqjLb.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

bodb = BigOlDB()
df_supported_coins = bodb.get_supported_coins()
df_supported_sectors = bodb.get_supported_sectors()

graph = agg()

app.layout = html.Div([
	dbc.NavbarSimple(
		children=[
			dbc.NavItem(dbc.NavLink("Link", href="#")),
			
		],
		brand="Demo",
		brand_href="#",
		sticky="top",
	),

	html.Div([

		html.Div([
			dcc.Dropdown(
				id='coin-ticker',
				style={
					'fontColor': 'blue',
					'display': 'inline-block'},
				className='dropdown',
				options=[{'label': row["Ticker"], 'value': row["Ticker"]} \
					for i, row in df_supported_coins.iterrows()],
				value='BTC'),
			dcc.Dropdown(
				id='sector-ticker',
				style={
					'fontColor': 'blue',
					'display': 'inline-block'},
				className='dropdown',
				options=[{'label': '{} - {}'.format(row['SectorTicker'], 
					row['SectorName']), 'value': row['SectorTicker']} \
					for i, row in df_supported_sectors.iterrows()],
				value='XPA')
			]),

		html.Div([
			dcc.RadioItems(
				id='currency-type',
				className='hud',
				options=[{'label': i, 'value': i} for i in ['USD', 'BTC']],
				value='USD',
				labelStyle={'display': 'inline-block'},
				style={
					# 'padding': 10,
					'width': '33%', 
					'display': 'inline-block'}), 
			dcc.Checklist(
				id='checklist-average',
				className='hud',
				options=[
					{'label': 'Short MA', 'value': 'sma'},
					{'label': 'Long MA', 'value': 'lma'},
					{'label': 'Exponential MA', 'value': 'ema'}
				],
				values=['sma', 'lma', 'ema'],
				style={
					# 'padding': 10,
					'width': '34%', 
					'display': 'inline-block',
				}),
			dcc.Checklist(
				id='candlestick',
				className='hud',
				options=[{'label': 'Candlestick', 'value': 'candlestick'}],
				values=[True],
				labelStyle={'display': 'inline-block'},
				style={
					# 'padding': 10,
					'width': '33%', 
					'display': 'inline-block',
				})
		],
		style={
			'width': '100%', 
			'display': 'inline-block'}),
		

	]),
	dcc.Graph(id='indicator-graphic', className='graph')], 
)

@app.callback(
	dash.dependencies.Output('indicator-graphic', 'figure'),
	[dash.dependencies.Input('coin-ticker', 'value'),
	 dash.dependencies.Input('currency-type', 'value'),
	 dash.dependencies.Input('checklist-average', 'values'),
	 dash.dependencies.Input('candlestick', 'values')])
def update_graph(ticker, currency_type, requested_mas, candlestick, candlestick_window=24):

	fig = graph.get_fig(ticker, currency_type, requested_mas, 
					candlestick=True, short_window=60, long_window=200)



	fig['layout'].update(
		title=ticker,
		font=styles.tickfont,
		autosize=True,
		paper_bgcolor=styles.base_colors['transparent'],
		plot_bgcolor=styles.base_colors['transparent'],
		titlefont=styles.tickfont,
		legend=styles.graph_layout['legend'],
		grid={'rows': 5},
		xaxis=styles.graph_layout['xaxis'],
		yaxis3=styles.graph_layout['yaxis3'],			
		yaxis2=styles.graph_layout['yaxis2'],
		yaxis=styles.graph_layout['yaxis']
	),


	return fig

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('-p', '--port_number', dest='port_number',
		help='Enter a fucking port number', default=8050)
	args = parser.parse_args()

	app.run_server(port=args.port_number, debug=True)
