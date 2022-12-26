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

carousel = dbc.Carousel(
    items=[
        {"key": "1", "src": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Plotly-logo.png"},
        {"key": "2", "src": "/static/images/image2.jpg"},
        {"key": "3", "src": "/static/images/image3.png"},
    ],
    controls=False,
    indicators=False,
    interval=2000,
    ride="carousel",
)

app.layout = html.Div([ navbar,
    carousel,
  dcc.Location(id='url', refresh=False),
  html.Div(id='page-content')
                     ])

if __name__ == '__main__':
    app.run_server()