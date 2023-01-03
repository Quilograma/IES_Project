import requests
from requests.auth import HTTPDigestAuth
import json
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output,State
import plotly.graph_objects as go
import pandas as pd
import datetime
import dash_bootstrap_components as dbc
from flask import Flask
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
from connect_mysql import cursor


logged=True

REFRESH_RATE_SECONDs=1
server = Flask(__name__)
app = dash.Dash(server=server,suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.ZEPHYR])

app.layout = html.Div([
  dcc.Location(id='url', refresh=False),
  html.Div(id='page-content')])

centered= {
      'position': 'fixed',
      'top': '50%',
      'left': '50%',
      'transform': 'translate(-50%, -50%)',
      'textAlign':'center'
    }

############# index_page ########################
index_page=html.Div([dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Sign in", href="/login_page")),
        dbc.NavItem(dbc.NavLink("Sign up", href="/sign_up"))
    ],
    brand='Dashboard',
    brand_href="/dashboard",
    color="primary",
    dark=True,
),
dbc.Container([
    dbc.Alert(
            [
                html.H1('Welcome to the website traffic monitoring tool!')
            ],
            color="info",
            className="d-flex align-items-center",
        style={'margin-top':'50px'}),
html.Div(style={'height':'100px'}),
dbc.Row([
    dbc.Col([html.Img(src='/assets/chart-line-solid.svg',className="img-fluid")],width=4),
    dbc.Col([html.Img(src='/assets/chart-pie-solid.svg',className="img-fluid")],width=4),
    dbc.Col([html.Img(src='/assets/arrows-spin-solid.svg',className='img-fluid')],width=4)
]),
dbc.Row([
    dbc.Col(html.P('Forecast the incoming traffic on each website with Machine Learning models.'),width=4),
    dbc.Col(html.P('Data Analytics in real time.'),width=4),
    dbc.Col(html.P('Monitor model metrics in real time and trigger a retraining process whenever you feel the model is not capturing distribution shifts.'),width=4)
])],fluid=True,style={'textAlign':'Center'})])

############ Sign up page #################
signup_page=html.Div([
    dbc.Label('Username:'),
    dbc.InputGroup([
        dbc.Input(type='text',id='sign_up_username',placeholder='Choose your username',className="mb-3")
    ]),
    dbc.Label('Password:'),
    dbc.InputGroup([
        dbc.Input(type='password',id='sign_up_password',placeholder='Choose your password (at least 6 characters)',className="mb-3")
    ]),
    dbc.Button('Submit',id='sign_up_btn_submit',className="mb-3",n_clicks=0),
    html.Div(id='sign_up_dummy')
],style=centered)

############# login page ###################
login_page=html.Div([
    dbc.Label('Username:'),
    dbc.InputGroup([
        dbc.Input(type='text',id='sign_in_username',placeholder='Choose your username',className="mb-3")
    ]),
    dbc.Label('Password:'),
    dbc.InputGroup([
        dbc.Input(type='password',id='sign_in_password',valid=False,placeholder='Choose your password (at least 6 characters)',className="mb-3")
    ]),
    dbc.Button('Submit',id='sign_in_btn_submit',className="mb-3",n_clicks=0),
    html.Div(id='sign_in_dummy')
],style=centered)

########## dashboard ################
dashboard=dbc.Container([
        dcc.Interval(
            id='interval-component',
            interval=REFRESH_RATE_SECONDs*1000, # in milliseconds
            n_intervals=0
        ),
    dbc.Tabs(id="tabs", children=[
        dbc.Tab(label='Data Table', tab_id='tab-1'),
        dbc.Tab(label='Data Analytics', tab_id='tab-2'),
        dbc.Tab(label='Training', tab_id='tab-3'),
        dbc.Tab(label='Forecasting',tab_id='tab-4'),
        dbc.Tab(label='Models history', tab_id='tab-5'),
    ],active_tab="tab-1"),
dbc.Container(id='select-tab',className='mt-3')])

dashboard_content=dbc.Container([
    dbc.Container([
        html.H3('Pick a desired refresh rate in seconds',style={'textAlign': 'center'})
       ],fluid = True),
        dcc.Slider(1, 60, value=5,id='my-slider',
        marks={
        1: {'label': '1'},
        5: {'label': '5'},
        20: {'label': '20'},
        40: {'label': '40'},
        60: {'label':'60'}
    }),
    dbc.Container([
        dbc.Row([
        dbc.Col([
        html.H3(id='live-update-text-currentRR',style={'font-weight': 'bold','textAlign':'center'}),
        html.H3(id='live-update-text',style={'textAlign': 'center'})],width=12)],className = "six column", style = {"margin-bottom": "25px"}),
        ],fluid= True),

    dbc.Container([
        dbc.Container([
        html.P('Visitors content table',style={'textAlign': 'center'}),
        dbc.Container(id='live-update-graph'),
        dbc.Pagination(id='pagination',active_page=1,max_value=5,fully_expanded=False, first_last=True, previous_next=True)])])
])

dashboard_analytics=dbc.Container([
    dbc.Container([
        dbc.Row([
        dbc.Col([
        dbc.Label('Select page id',),
        dcc.Dropdown([i+1 for i in range(10)], '1', id='choose-page_id-dropdown'),
        dbc.Label('Select group by'),
        dcc.Dropdown(options=[
        {'label':'Hour','value':'H'},
       {'label': 'Day', 'value': 'D'},
       {'label': 'Week', 'value': 'W'},
       {'label': 'Month', 'value': 'M'},
   ], value='H', id='choose-groupby-dropdown'),
        dbc.Label('Filter by datetime '),
        dcc.DatePickerRange(
        id='filterbydate',
        end_date=datetime.datetime.now().date(),
        start_date=datetime.datetime.now().date()
    )],width=3),    
    dbc.Col([
        dcc.Graph(id='live-update-graph-timeseries')],width=9)
        ])],fluid=True)])

dashboard_training=dbc.Container([
        dbc.Row([
        dbc.Col([
            dbc.Label('Select Page Id'),
            dcc.Dropdown([i+1 for i in range(10)], '1', id='input_pageid'),
            dbc.Label('Select number of lags'),
            dbc.Input(id='input_lags'),
            dbc.Label('Select forecast period'),
            dbc.Input(id='input_forecastperiod'),
            dbc.Label('Select the maximum miscoverage rate'),
            dbc.Input(id='input_miscoveragerate',className='mb-3'),
            dbc.Container([
            dbc.Button('Submit',id='train-submit-btn',n_clicks=0,className='mt-3')
            ],style={'textAlign':'center'})
        ],width={"size": 4, "offset": 4})]),
        dcc.Loading(children=html.Div(id="loading-training"),fullscreen=True)
],style=centered)

dashboard_forecast= dbc.Container(dbc.Row(dbc.Col([dbc.Label('Select Page id'),dcc.Dropdown([i+1 for i in range(10)], '1', id='input_pageid_forecast'), dbc.Container([
            dbc.Button('Forecast',color='danger',id='forecast-submit-btn',n_clicks=0,className='mt-3')
            ],style={'textAlign':'center'}),dbc.Container(id='forecast-txt')],width={"size": 4, "offset": 4})))

dashboard_modelhistoric=dbc.Container([dbc.Label('Select page id'),
dcc.Dropdown([i+1 for i in range(10)], '1', id='input_pageid_history',className='mb-3'),
dbc.Container(id='model-container'), 
dbc.Pagination(id='pagination-model-history',active_page=1,className='mt-3',max_value=5,fully_expanded=False, first_last=True, previous_next=True)])

########### callbacks #################

@app.callback(Output('model-container','children'),Output('pagination-model-history','max_value'),Input('pagination-model-history','active_page'),Input('interval-component', 'n_intervals'),Input('input_pageid_history','value'))
def filter_by_pageid(active_page,n,pageid):
        url = 'http://myapp:5000/Models/'+str(pageid)
        r = requests.get(url, auth=HTTPDigestAuth('martim', 'martimpw'),timeout=10)
        model_table = pd.DataFrame.from_dict(json.loads(r.text))
        n_rows=model_table.shape[0]

        if n_rows==0:
            return dbc.Alert(
            [
                html.H1('There are no models for page id {}'.format(pageid))
            ],
            color="info",
            className="mt-3"),1
        else:

            model_table['TrainingStart']=pd.to_datetime(model_table['TrainingStart'])
            model_table_sorted = model_table.sort_values(by=['TrainingStart'], ascending=False)
            n_pages=int(n_rows/50)
            last_page=n_rows%50

            if last_page>0:
                n_pages+=1
            
            if active_page<n_pages:
                model_table_sorted=model_table_sorted.iloc[50*(active_page-1):50*active_page,:]
            else:
                model_table_sorted=model_table_sorted.iloc[50*(active_page-1):,:]
        
            model_table_sorted['TrainingStart']=model_table_sorted['TrainingStart'].apply(lambda x: x.strftime("%m-%d-%Y %H:%M:%S"))

            model_table_sorted_bootstrap=dbc.Table.from_dataframe(model_table_sorted, striped=True, bordered=True, hover=True)
        
            return model_table_sorted_bootstrap,n_pages


@app.callback(Output('loading-training','children'),Input('train-submit-btn','n_clicks'),
 State('input_lags','value'),
    State('input_forecastperiod','value'),
    State('input_miscoveragerate','value'),
    State('input_pageid','value'))

def loading_state(n_clicks,lags,forecastperiod,alpha,pageid):
    d={}
    d['lags']=lags
    d['forecastperiod']=forecastperiod
    d['alpha']=alpha
    d['page_id']=pageid

    if n_clicks>0:
        url = 'http://myapp:5000/train'
        r = requests.post(url, auth=HTTPDigestAuth('martim', 'martimpw'),json=d,timeout=10)
    return ''

@app.callback(Output('page-content', 'children'),
[Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/login_page':
        return login_page
    elif pathname == '/dashboard' and logged:
        return dashboard
    elif pathname == 'signup_page':
        return signup_page
    else:
        return index_page

@app.callback(Output('select-tab','children'),Input('tabs','active_tab'))
def render_tab(tab):
    if tab=='tab-1':
        return dashboard_content
    elif tab=='tab-2':
        return dashboard_analytics
    elif tab=='tab-3':
        return dashboard_training
    elif tab=='tab-4':
        return dashboard_forecast
    elif tab=='tab-5':
        return dashboard_modelhistoric


@app.callback(Output('interval-component','interval'),Input('my-slider', 'value'))
def update_refresh_rate(input):
    return input*1000

@app.callback(Output('live-update-text-currentRR','children'),Input('my-slider', 'value'))
def current_RR(input):
    return 'Current refresh rate: {}'.format(input)



@app.callback([Output('pagination','max_value'),Output('live-update-graph', 'children'),Output('live-update-text','children')],
              Input('interval-component', 'n_intervals'),Input('pagination', 'active_page'))

def update_graph_live(n,active_page):
    url = 'http://myapp:5000/Visitors'
    r = requests.get(url, auth=HTTPDigestAuth('martim', 'martimpw'),timeout=10)
    df_data= pd.DataFrame.from_dict(json.loads(r.text))
    df_data_sorted = df_data.sort_values(by=['id'], ascending=False)
    
    time_now=datetime.datetime.now()
    formated_time=time_now.strftime("%m-%d-%Y %H:%M:%S")
    n_rows = df_data_sorted.shape[0]
    n_pages=int(n_rows/50)
    last_page=n_rows%50

    if last_page>0:
        n_pages+=1
    if active_page<n_pages:
        df_data_sorted=df_data_sorted.iloc[50*(active_page-1):50*active_page,:]
    else:
        df_data_sorted=df_data_sorted.iloc[50*(active_page-1):,:]
    
    table = dbc.Table.from_dataframe(df_data_sorted, striped=True, bordered=True, hover=True)

    return n_pages,table,[html.Span('Last refreshed at {}'.format(formated_time))]

@app.callback(Output('live-update-graph-timeseries','figure'),[Input('choose-page_id-dropdown','value'),Input('choose-groupby-dropdown','value'),Input('interval-component', 'n_intervals'),Input('filterbydate', 'start_date'),
    Input('filterbydate', 'end_date')])
def update_graph_timeseries(dropdown_value,groupby_drop,n,start_date,end_date):
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')+datetime.timedelta(days=1)
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    url = 'http://myapp:5000/Visitors?page_id='+str(dropdown_value)
    r = requests.get(url, auth=HTTPDigestAuth('martim', 'martimpw'),timeout=10)
    df_data= pd.DataFrame.from_dict(json.loads(r.text))

    df_data['accessed_at'] = pd.to_datetime(df_data['accessed_at'])
    mask = (df_data['accessed_at'] >= start_date) & (df_data['accessed_at'] <= end_date)
    df_data=df_data.loc[mask]
    df_counts=df_data.groupby([pd.Grouper(key='accessed_at', freq=groupby_drop)]).count()
    df_counts.reset_index(inplace=True)
    fig = px.line(df_counts, x='accessed_at', y='page_id',title="Accesses for page id {} from {} to {} by {}".format(dropdown_value,start_date.date(),end_date.date(),groupby_drop),
    labels={'page_id':'#visitors'})
    time_now=datetime.datetime.now()
    formated_time=time_now.strftime("%m-%d-%Y %H:%M:%S.%f")
    fig.update_layout(xaxis_range=[df_counts['accessed_at'].min(),formated_time])
    return fig

@app.callback(Output('forecast-txt','children'),Input('forecast-submit-btn','n_clicks'),Input('input_pageid_forecast','value'))
def forecast(n_clicks,pageid):

    if n_clicks>0:
        url = 'http://myapp:5000/forecast/'+str(pageid)
        r = requests.get(url, auth=HTTPDigestAuth('martim', 'martimpw'),timeout=10)
        return r.text
    else:
        return ''

"""
@app.callback(Output('train_div','style'),Output('TrainSubmit','style'),Output('TrainButton','children'),Output('TrainButton','style'),[Input('TrainButton','n_clicks')])
def toogle_form(n_clicks):
    if n_clicks%2!=0:
        return {'display':'block'},{'display':'inline','textAlign': 'center','background-color':'orange','textAlign': 'center','margin-top':'10px'},'Hide',{'textAlign': 'center','background-color': 'red','margin-top':'10px'}
    else:
        return {'display':'none'},{'display':'none','textAlign': 'center','background-color':'green','textAlign': 'center','margin-top':'10px'},'Train a model',{'textAlign': 'center','background-color': '#008CBA','margin-top':'10px'}

@app.callback(Output('live-update-graph-prection','figure'),Input('TrainSubmit','n_clicks'),
    State('input_lags','value'),
    State('input_forecastperiod','value'),
    State('input_miscoveragerate','value'),
    State('input_pageid','value'))

def train_forecast(n_clicks,lags,forecastperiod,alpha,pageid):
    d={}
    d['lags']=lags
    d['forecastperiod']=forecastperiod
    d['alpha']=alpha
    d['page_id']=pageid
    fig = go.Figure()

    if n_clicks>0:
        url = 'http://myapp:5000/train'
        r = requests.post(url, auth=HTTPDigestAuth('martim', 'martimpw'),json=d,timeout=10)
        d_forecast=json.loads(r.text)
        lower_bound=d_forecast['lower_bound']
        upper_bound=d_forecast['upper_bound']
        x_axis=[i for i in range(len(lower_bound))]
        fig.add_trace(go.Scatter(x=x_axis, y=lower_bound,name='lower bound', mode='lines+markers', line_color='blue', fill='tozerox',fillcolor='lightgray')) # fill down to xaxis
        fig.add_trace(go.Scatter(x=x_axis, y=upper_bound,name='upper bound', mode='lines+markers',line_color='blue' ,fill='tonexty',fillcolor='lightgray'))
        return fig
    else:
        return fig
"""

""" @app.callback(Output('sign_up_dummy','children'),Output('url', 'pathname'),Input('sign_up_btn_submit','n_clicks'),State('sign_up_username','value'),State('sign_up_password','value'))

def sign_up(n_clicks,username,password):
    check=False
    pathname='/'

    if n_clicks>0:

        cursor.execute(
            '''
            SELECT * FROM users
            where username=?;
            '''
        ,(username))

        list_user=cursor.fetchall()

        if len(list_user)== 0 and len(password)>6:
            cursor.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, password))
            check=True
            pathname='/'

    return str(check),pathname


@app.callback(Output('sign_in_dummy','children'),Output('url', 'pathname'),Input('sign_in_btn_submit','n_clicks'),State('sign_in_username','value'),State('sign_in_password','value'))

def sign_in(n_clicks,username,password):
    check=False
    pathname='/home'

    if n_clicks>0:

        cursor.execute(
            '''
            SELECT * FROM users
            where username=?;
            '''
        ,(username))

        list_user=cursor.fetchall()

        if len(list_user)>0:
            real_pw=list_user[0][0]

            if password==real_pw:
                check=True
                pathname='/dashboard'
                logged=True

    return str(check),pathname """

if __name__ == '__main__':
    app.run_server()