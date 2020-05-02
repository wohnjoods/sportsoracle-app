import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

#from dash.dependencies import Input, Output

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['assets/custom.css',dbc.themes.SUPERHERO,'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                url_base_pathname='/')
#server = app.server
app.config.suppress_callback_exceptions = True
if __name__ == '__main__':
    app.run_server(debug=True)
