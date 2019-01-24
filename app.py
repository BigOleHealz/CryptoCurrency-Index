#!/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from styles import style_dicts
import aggregator_functions as agg
from big_ol_db import BigOlDB

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
                options=[{'label': row["Ticker"], 'value': row["Ticker"]} for i, row in df_supported_coins.iterrows()],
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

    dcc.Graph(id='indicator-graphic')], 
    style={'backgroundColor':style_dicts.colors['background']}
)

@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('coin-ticker', 'value'),
     dash.dependencies.Input('currency-type', 'value'),
     dash.dependencies.Input('checklist-average', 'values') ])
def update_graph(ticker, currency_type, requested_mas):

    quotes = bodb.get_minutely_coin_data(ticker)

    data, y_min, y_max = agg.get_traces(quotes, currency_type, requested_mas, 
                            short_window=60, long_window=200)

    layout = go.Layout(
            xaxis={
                'title': 'Date/Time',
                'showticklabels': True,
                'titlefont': style_dicts.axis_label_font,
                'tickfont': style_dicts.tick_font,
                'exponentformat': 'e',
                'showexponent': 'all',
                # 'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': "{} Price - {}".format(ticker, currency_type),
                'type': 'linear',
                'titlefont': style_dicts.axis_label_font,
                'tickfont': style_dicts.tick_font,
                'exponentformat': 'e',
                'showexponent': 'all',
                # 'range': [y_min, y_max],
                'side': 'left'
            },
            # yaxis2={
            #     'title': "{} Price - {}".format(ticker, currency_type),
            #     'type': 'linear',
            #     'titlefont': style_dicts.axis_label_font,
            #     'tickfont': style_dicts.tick_font,
            #     'exponentformat': 'e',
            #     'showexponent': 'all',
            #     # 'range': [y_min, y_max],
            #     'overlaying': 'y',
            #     'side': 'right'
            # },
            margin=style_dicts.graph_margins,
            hovermode='closest',
            plot_bgcolor=style_dicts.colors['background'],
            paper_bgcolor=style_dicts.colors['background'],
            legend=style_dicts.legend_format,
        )


    return {
        'data': data,
        'layout': layout
    }


if __name__ == '__main__':
    app.run_server(port=8072, debug=True)
