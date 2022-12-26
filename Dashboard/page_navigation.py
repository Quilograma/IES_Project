from dash import dcc, html
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output,State

app = dash.Dash('app',suppress_callback_exceptions=True)

app.layout = html.Div([
  dcc.Location(id='url', refresh=False),
  html.Div(id='page-content')
                     ])

index_page = html.Div([
html.Div(
dcc.Input(id="user", type="text", placeholder="Enter Username",className="inputbox1",
style={'margin-left':'35%','width':'450px','height':'45px','padding':'10px','margin-top':'60px',
'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'
}),
),
html.Div(
dcc.Input(id="passw", type="text", placeholder="Enter Password",className="inputbox2",
style={'margin-left':'35%','width':'450px','height':'45px','padding':'10px','margin-top':'10px',
'font-size':'16px','border-width':'3px','border-color':'#a0a3a2',
}),
),
html.Div(
html.Button('Verify', id='verify', n_clicks=0, style={'border-width':'3px','font-size':'14px'}),
style={'margin-left':'45%','padding-top':'30px'}),
html.Div(id='output1')
])

next_page = html.Div([
html.Div(dcc.Link('Log out', href='/',style={'color':'#bed4c4','font-family': 'serif', 'font-weight': 'bold', "text-decoration": "none",'font-size':'20px'}),style={'padding-left':'80%','padding-top':'10px'}),
        html.H1(children="This is the Next Page, the main Page",className="ap",style={
 'color':'#89b394','text-align':'center','justify':'center','padding-top':'170px','font-weight':'bold',
 'font-family':'courier',
 'padding-left':'1px'  })])

@app.callback(Output('page-content', 'children'),
[Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/next_page':
        return next_page
    else:
        return index_page

@app.callback(
    Output('output1', 'children'),
   [Input('verify', 'n_clicks')],[State('user', 'value'),
                State('passw', 'value')])
def update_output(n_clicks, uname, passw):
    li={'user':'pw123'}
    if uname =='' or uname == None or passw =='' or passw == None:
        return html.Div(children='',style={'padding-left':'550px','padding-top':'10px'})
    if uname not in li:
        return html.Div(children='Incorrect Username',style={'padding-left':'550px','padding-top':'40px','font-size':'16px'})
    if li[uname]==passw:
        return html.Div(dcc.Link('Access Granted!', href='/next_page',style={'color':'#183d22','font-family': 'serif', 'font-weight': 'bold', "text-decoration": "none",'font-size':'20px'}),style={'padding-left':'605px','padding-top':'40px'})
    else:
        return html.Div(children='Incorrect Password',style={'padding-left':'550px','padding-top':'40px','font-size':'16px'})

if __name__ == '__main__':
    app.run_server(debug=True)