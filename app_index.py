#!/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from constants import style_dicts as styles
from aggregator_functions import AggregatorFunctions as agg
from big_ol_db import BigOlDB
from argparse import ArgumentParser

app = dash.Dash(__name__)

bodb = BigOlDB()
df_supported_sectors = bodb.get_supported_sectors()

graph = agg()

app.layout = html.Div([
	html.Div([

		html.Div([
			dcc.Dropdown(
				id='coin-ticker',
				className='dropdown',
				options=[{'label': row["sectorName"], 'value': row["sectorTicker"]} \
					for i, row in df_supported_sectors.iterrows()],
				value='XPA'
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
	 # dash.dependencies.Input('currency-type', 'value'),
	 # dash.dependencies.Input('checklist-average', 'values'),
	 # dash.dependencies.Input('candlestick', 'values')]
	 ])
def update_graph(ticker):

	fig = graph.get_fig(ticker)

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
				'buttons': styles.range_selector_buttons['buttons']},
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
			'domain':[styles.graph_layout['domains']['y2_top'] + \
				styles.graph_layout['domains']['padding'], 1],
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
			'domain':[styles.graph_layout['domains']['y2_bottom'], 
				styles.graph_layout['domains']['y2_top']], 
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
			'domain':[0, styles.graph_layout['domains']['y2_bottom'] - \
				styles.graph_layout['domains']['padding']], 
			'anchor': 'y3'}
		),

	return fig

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('-p', '--port_number', dest='port_number',
		help='Enter a fucking port number', default=8050)
	args = parser.parse_args()

	app.run_server(port=args.port_number, debug=True)
