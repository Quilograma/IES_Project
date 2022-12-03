import requests
from requests.auth import HTTPDigestAuth
import json
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import datetime

REFRESH_RATE_SECONDs=1
app = dash.Dash(__name__)
app.layout = html.Div([

    html.Div([
        html.Div([
        html.H1('MyDashboard',style={'textAlign': 'center'}),
        html.H3('Pick a desired refresh rate in seconds',style={'textAlign': 'center'}),
       ],id = "header", className = "six column", style = {"margin-bottom": "25px"}),
       ],className = "row flex-display"),
        dcc.Slider(1, 60, value=5,id='my-slider',
        marks={
        1: {'label': '1'},
        5: {'label': '5'},
        20: {'label': '20'},
        40: {'label': '40'},
        60: {'label':'60'}
    }),

    html.Div([
        html.Div([
        html.H3(id='live-update-text-currentRR',style={'font-weight': 'bold','textAlign':'center'}),
        html.H3(id='live-update-text',style={'textAlign': 'center'})],className = "six column", style = {"margin-bottom": "25px"}),
        ],className = "row flex-display"),

    html.Div([
        html.Div([
        dcc.Graph(id='live-update-graph',config = {'displayModeBar': 'hover'})], className="create_container full columns")]
        ,className="row flex-display"),
        dcc.Interval(
            id='interval-component',
            interval=REFRESH_RATE_SECONDs*1000, # in milliseconds
            n_intervals=0
        ),
    html.Div([
        html.Div([
        html.P('Select page id',className = 'fix_label'),
        dcc.Dropdown([i+1 for i in range(10)], '1', id='choose-page_id-dropdown'),
        html.P('Select group by',className = 'fix_label'),
        dcc.Dropdown(options=[
        {'label':'Hour','value':'H'},
       {'label': 'Day', 'value': 'D'},
       {'label': 'Week', 'value': 'W'},
       {'label': 'Month', 'value': 'M'},
   ], value='H', id='choose-groupby-dropdown')],className = "create_container three columns"),
        html.Div([
        dcc.Graph(id='live-update-graph-timeseries')],className = "create_container nine columns")
        ],className = "row flex-display")
    ],id = "mainContainer", style = {"display": "flex", "flex-direction": "column"})

@app.callback(Output('interval-component','interval'),Input('my-slider', 'value'))
def update_refresh_rate(input):
    return input*1000

@app.callback(Output('live-update-text-currentRR','children'),Input('my-slider', 'value'))
def current_RR(input):
    return 'Current refresh rate: {}'.format(input)

@app.callback([Output('live-update-graph', 'figure'),Output('live-update-text','children')],
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    url = 'http://localhost:5001/Visitors'
    r = requests.get(url, auth=HTTPDigestAuth('martim', 'martimpw'),timeout=10)
    df_data= pd.DataFrame.from_dict(json.loads(r.text))
    df_data_sorted = df_data.sort_values(by=['id'], ascending=False)
    df_data_sorted=df_data_sorted.iloc[:10,:]
    fig = go.Figure(data=[go.Table(header=dict(values=list(df_data_sorted.columns)),
                 cells=dict(values=df_data_sorted.values.T))
                     ])
    time_now=datetime.datetime.now()
    formated_time=time_now.strftime("%m-%d-%Y %H:%M:%S")
    return fig,[html.Span('Last refreshed at {}'.format(formated_time))]

@app.callback(Output('live-update-graph-timeseries','figure'),[Input('choose-page_id-dropdown','value'),Input('choose-groupby-dropdown','value'),Input('interval-component', 'n_intervals')])
def update_graph_timeseries(dropdown_value,groupby_drop,n):
    url = 'http://localhost:5001/Visitors?page_id='+str(dropdown_value)
    r = requests.get(url, auth=HTTPDigestAuth('martim', 'martimpw'),timeout=10)
    df_data= pd.DataFrame.from_dict(json.loads(r.text))
    df_data['accessed_at'] = pd.to_datetime(df_data['accessed_at'])
    df_counts=df_data.groupby([pd.Grouper(key='accessed_at', freq=groupby_drop)]).count()
    df_counts.reset_index(inplace=True)
    fig = px.line(df_counts, x='accessed_at', y='page_id',title="Automatic Labels Based on Data Frame Column Names",
    labels={'page_id':'#visitors'})
    time_now=datetime.datetime.now()
    formated_time=time_now.strftime("%m-%d-%Y %H:%M:%S")
    fig.update_layout(xaxis_range=[df_counts['accessed_at'].min(),formated_time])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)