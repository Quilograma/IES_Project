import base64
from dash import dcc, html
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output,State


external_stylesheets = [dbc.themes.ZEPHYR,
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
                       ]
app = dash.Dash('app',suppress_callback_exceptions=True,external_stylesheets = external_stylesheets)

centered= {
      'position': 'fixed',
      'top': '50%',
      'left': '50%',
      'transform': 'translate(-50%, -50%)',
      'textAlign':'center'
    }

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Sign in", href="/login_page")),
        dbc.NavItem(dbc.NavLink("Sign up", href="#"))
    ],
    brand='Dashboard',
    brand_href="#",
    color="primary",
    dark=True,
)





head=dbc.Container([
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
])],fluid=True,style={'textAlign':'Center'})


index_page=html.Div([navbar,head])

app.layout = html.Div([
  dcc.Location(id='url', refresh=False),
  html.Div(id='page-content')
                     ])
login_page=html.Div([
    html.P('Username:'),
    dbc.InputGroup([
        dbc.Input(type='text',id='username',placeholder='Choose your username',className="mb-3")
    ]),
    html.P('Password:'),
    dbc.InputGroup([
        dbc.Input(type='password',id='password',valid=False,placeholder='Choose your password (at least 6 characters)',className="mb-3")
    ]),
    dbc.Button('Submit',id='btn_submit',className="mb-3",n_clicks=0)

],style=centered)

@app.callback(Output('page-content', 'children'),
[Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/login_page':
        return login_page
    else:
        return index_page

@app.callback(Output('password','valid'),Input('btn_submit','n_clicks'),State('username','value'),State('password','value'))

def login(n_clicks,username,password):
    check_password=False

    if n_clicks>0:
        if len(password)>6:
            check_password=True
        else:
            check_password=False

    return check_password

if __name__ == '__main__':
    app.run_server()