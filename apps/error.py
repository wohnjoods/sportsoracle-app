import dash_core_components as dcc
import dash_html_components as html
import dash_table
from components.header import Header
import components.printButton
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd

######################## 404 Page ########################
errorpage = html.Div([
    # CC Header
    Header(),
    html.P(["404 Page not found"])
], className="no-page")
######################## End 404 Page #####################
