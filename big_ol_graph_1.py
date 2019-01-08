#!/usr/bin/env python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from styles import style_dicts
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
            ),
            dcc.RadioItems(
                id='currency-type',
                options=[{'label': i, 'value': i} for i in ['USD', 'BTC']],
                value='USD',
                labelStyle={'display': 'inline-block'}
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
     dash.dependencies.Input('currency-type', 'value')])
def update_graph(ticker, currency_type):

    price_data = bodb.get_minutely_coin_data(ticker)

    return {
        'data': [go.Scatter(
            x=price_data['TimeStampID'],
            y=price_data['Price_{}'.format(currency_type)],
            mode='lines',
        )],
        'layout': go.Layout(
            xaxis={
                'title': 'Date/Time',
                'showticklabels': True,
                'titlefont': style_dicts.axis_label_font,
                'tickfont': style_dicts.tick_font,
                'exponentformat': 'e',
                'showexponent': 'all',
                # 'tickformat': '%m/%y'
                # 'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': "{} Price - {}".format(ticker, currency_type),
                'type': 'linear',
                'titlefont': style_dicts.axis_label_font,
                'tickfont': style_dicts.tick_font,
                'exponentformat': 'e',
                'showexponent': 'all'
            },
            margin=style_dicts.graph_margins,
            hovermode='closest',
            plot_bgcolor=style_dicts.colors['background'],
            paper_bgcolor=style_dicts.colors['background'],
        )
    }


if __name__ == '__main__':
    app.run_server(port=8061, debug=True)








