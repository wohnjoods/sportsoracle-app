import collections
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import sys
import os
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components.header import Header
from components.printButton import print_button
import plotly
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd
from components.functions import read_sql_query
import copy
import numpy as np
import json
from dash.dependencies import Input, Output, State

from app import app


layout_home = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["This is the Alpha version of this application with only NCAA Basketball and it is under active development, but feel free to check out the tabs"],
                            style={'marginTop': 15})
                ])
            )
        ),
        
        

    ], className="subpage")
], className="page")
