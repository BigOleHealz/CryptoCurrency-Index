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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/YeqjLb.css'})

bodb = BigOlDB()
df_supported_coins = bodb.get_supported_coins()

graph = agg()

app.layout = html.Div([
	dbc.NavbarSimple(
		children=[
			dbc.NavItem(dbc.NavLink("Link", href="#")),
			dbc.DropdownMenu(
				nav=True,
				in_navbar=True,
				label="Menu",
				children=[
					dbc.DropdownMenuItem(coin) for coin in df_supported_coins['Ticker']
					# dbc.DropdownMenuItem(divider=True),
					# dbc.DropdownMenuItem("Entry 3"),
				],
			),
		],
		brand="Demo",
		brand_href="#",
		sticky="top",
	),

	html.Div([

		html.Div([
			dcc.Dropdown(
				id='coin-ticker',
				className='dropdown',
				options=[{'label': row["Ticker"], 'value': row["Ticker"]} \
					for i, row in df_supported_coins.iterrows()],
				value='BTC'
			)]),
		html.Div([
			dcc.RadioItems(
				id='currency-type',
				className='hud',
				options=[{'label': i, 'value': i} for i in ['USD', 'BTC']],
				value='USD',
				labelStyle={'display': 'inline-block'}
			), 
			dcc.Checklist(
				id='checklist-average',
				className='hud',
				options=[
					{'label': 'Short MA', 'value': 'sma'},
					{'label': 'Long MA', 'value': 'lma'},
					{'label': 'Exponential MA', 'value': 'ema'}
				],
				values=['sma', 'lma', 'ema']
			)
		],
		style={
			'width': '48%', 
			'display': 'inline-block', 
			'backgroundColor': styles.colors['background']}),
		html.Div([
			dcc.Checklist(
				id='candlestick',
				className='hud',
				options=[{'label': 'Candlestick', 'value': 'candlestick'}],
				values=[True],
				labelStyle={'display': 'inline-block'}
			)
		]),

	], 
	style={'backgroundColor':styles.colors['background']}),
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
		font={
			'family': 'verdana',
			'size': 15,
			'color': styles.colors['titlefont']
		},
		autosize=True,
		paper_bgcolor=styles.base_colors['transparent'],
		plot_bgcolor=styles.base_colors['transparent'],
		titlefont={
			'color': styles.colors['titlefont']
		},
		legend={
			'bgcolor': styles.colors['legend_bg'],
			'font': {
				'family': 'verdana',
				'color': styles.base_colors['black']
			}},
		grid={'rows': 5},
		xaxis={
			'title': 'Date',
			'titlefont': {
				'family': 'verdana',
				'size': 12,
				'color': styles.colors['titlefont']
			},
			'color': styles.colors['titlefont'],
			'tickangle': styles.graph_layout['tickangle'],
			'tickfont': styles.graph_layout['tickfont'],
			'gridcolor': styles.base_colors['grey'],
			'rangeslider': {'visible': False},
			'gridcolor': styles.colors['gridcolor'],
			'rangeselector': {
				'buttons': vals.range_selector_buttons['buttons']},
			},
		yaxis3={
			'title': 'RSi',
			'titlefont': {
				'family': 'verdana',
				'size': 8,
				'color': styles.colors['titlefont']
			},
			'color': styles.colors['titlefont'],
			'gridcolor': styles.colors['gridcolor'],
			'tickangle': styles.graph_layout['tickangle'],
			'tickcolor': styles.colors['background'], 
			'tickfont': styles.graph_layout['tickfont'],
			'domain':[vals.domains['y2_top'] + vals.domains['padding'], 1],
			'range': [-5, 105],
			'zeroline': False},			
		yaxis2={
			'title': 'Price USD',
			'titlefont': {
				'family': 'verdana',
				'size': 12,
				'color': styles.colors['titlefont']
			},
			'color': styles.colors['titlefont'],
			'gridcolor': styles.colors['gridcolor'],
			'tickangle': styles.graph_layout['tickangle'],
			'tickcolor': styles.colors['background'],
			'tickfont': styles.graph_layout['tickfont'],
			'domain': [vals.domains['y2_bottom'], vals.domains['y2_top']], 
			'anchor': 'y2'},
		yaxis={
			'title': 'Volume',
			'titlefont': {
				'family': 'verdana',
				'size': 8,
				'color': styles.colors['titlefont']
			},
			'color': styles.colors['titlefont'],
			'gridcolor': styles.colors['gridcolor'],
			'tickangle': styles.graph_layout['tickangle'],
			'tickcolor': styles.colors['background'], 
			'tickfont': styles.graph_layout['tickfont'],
			'domain':[0, vals.domains['y2_bottom'] - vals.domains['padding']], 
			'anchor': 'y3'}
		),


	return fig

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('-p', '--port_number', dest='port_number',
		help='Enter a fucking port number', default=8050)
	args = parser.parse_args()

	app.run_server(port=args.port_number, debug=True)
