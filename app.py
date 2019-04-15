#!/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from styles import style_dicts
import aggregator_functions as agg
from big_ol_db import BigOlDB
from argparse import ArgumentParser

external_stylesheets = ['styles/style_sheet.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/YeqjLb.css'})

bodb = BigOlDB()
df_supported_coins = bodb.get_supported_coins()

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='coin-ticker',
                options=[{'label': row["Ticker"], 'value': row["Ticker"]} \
                    for i, row in df_supported_coins.iterrows()],
                value='BTC'
            )]),
        html.Div([
            dcc.RadioItems(
                id='currency-type',
                options=[{'label': i, 'value': i} for i in ['USD', 'BTC']],
                value='USD',
                labelStyle={'display': 'inline-block'}
            ), 
            dcc.Checklist(
                id='checklist-average',
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
            'backgroundColor': style_dicts.colors['background']}),

    ], 
    style={'backgroundColor':style_dicts.colors['background']}),

    html.Div([
            dcc.Checklist(
                id='candlestick',
                options=[{'label': 'Candlestick', 'value': 'candlestick'}],
                values=[True],
                labelStyle={'display': 'inline-block'}
            )
        ]), 

    dcc.Graph(id='indicator-graphic')], 
)

@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('coin-ticker', 'value'),
     dash.dependencies.Input('currency-type', 'value'),
     dash.dependencies.Input('checklist-average', 'values'),
     dash.dependencies.Input('candlestick', 'values')])
def update_graph(ticker, currency_type, requested_mas, candlestick):

    quotes = bodb.get_minutely_coin_data(ticker)

    fig = agg.get_fig(quotes, currency_type, requested_mas, short_window=60, long_window=200)

    return fig


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port_number', dest='port_number',
        help='Enter a fucking port number', default=8050)
    args = parser.parse_args()

    app.run_server(port=args.port_number, debug=True)
