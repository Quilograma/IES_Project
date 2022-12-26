import base64
from dash import dcc, html
import dash
import dash_bootstrap_components as dbc

app = dash.Dash('app',suppress_callback_exceptions=True,external_stylesheets = [dbc.themes.ZEPHYR])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Sign in", href="#")),
        dbc.NavItem(dbc.NavLink("Sign up", href="#"))
    ],
    brand='Dashboard',
    brand_href="#",
    color="primary",
    dark=True,
)



head=html.Div([
html.H1('Welcome to the Website traffic monitoring tool!'),
dbc.Row([
    dbc.Col(html.Img(src='./assets/image3.png',className='img-fluid'),width=3),
    dbc.Col(html.P('col2'),width=3),
    dbc.Col(html.P('col3'),width=3)
])],style={'textAlign':'Center'})



app.layout = html.Div([navbar,
head,
  dcc.Location(id='url', refresh=False),
  html.Div(id='page-content')
                     ])

if __name__ == '__main__':
    app.run_server()