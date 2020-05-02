

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

#, layout_average_stats, layout_elo, layout_elo_accuracy, layout_spread_accuracy, layout_total_accuracy, layout_moneyline_accuracy, layout_spread_predictions, layout_total_predictions, layout_moneyline_predictions
import callbacks
# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-code/12463/2?u=dcomfort
#from app import server
from app import app
from apps.ncaab_boxscore import layout_boxscore
from apps.ncaab_average_stats import layout_average_stats
from apps.ncaab_rank import layout_rank
from apps.ncaab_rank_accuracy import layout_rank_accuracy
from apps.ncaab_total_accuracy import layout_total_accuracy#
from apps.ncaab_spread_predictions import layout_spread_predictions
from apps.ncaab_total_predictions import layout_total_predictions
from apps.ncaab_moneyline_predictions import layout_moneyline_predictions
from apps.ncaab_spread_accuracy import layout_spread_accuracy
from apps.ncaab_moneyline_accuracy import layout_moneyline_accuracy
from apps.home import layout_home
#from apps.ncaab_total_accuracy import layout_total_accuracy
from apps.error import errorpage

# see https://dash.plot.ly/external-resources to alter header, footer and favicon
#right now it is commented out and doing nothing?
app.index_string = ''' 
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Sports Oracle</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
# Update page
# # # # # # # # #

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return layout_home
    elif pathname == '/ncaab/boxscore/':
        return layout_boxscore
    elif pathname == '/ncaab/average-stats/':
       #only have one layout at a time for quicker testing, commented out import too
        return layout_average_stats
    elif pathname == '/ncaab/rank/':
        return layout_rank
    elif pathname == '/ncaab/rank/accuracy/':
        return layout_rank_accuracy
    elif pathname == '/ncaab/betting/spread/accuracy/':
        return layout_spread_accuracy
    elif pathname == '/ncaab/betting/total/accuracy/':
        return layout_total_accuracy
    elif pathname == '/ncaab/betting/moneyline/accuracy/':
        return layout_moneyline_accuracy
    elif pathname == '/ncaab/betting/spread/predictions/':
        return layout_spread_predictions
    elif pathname == '/ncaab/betting/total/predictions/':
        return layout_total_predictions
    elif pathname == '/ncaab/betting/moneyline/predictions/':
        return layout_moneyline_predictions
    else:
        return errorpage


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "https://codepen.io/bcd/pen/KQrXdb.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://codepen.io/dmcomfort/pen/JzdzEZ.css"]
#for css in external_css:
#    app.css.append_css({"external_url": css})

external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
               "https://codepen.io/bcd/pen/YaXojL.js"]

#for js in external_js:
#    app.scripts.append_script({"external_url": js})

if __name__ == '__main__':
    app.run_server(debug=True)
