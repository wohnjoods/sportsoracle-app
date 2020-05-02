

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
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd
from components.functions import read_sql_query
from dash.dependencies import Input, Output

from app import app

####################### Read in data ############################
#read in 2020 by default, refresh for anything else
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker
db = 'ncaab'  # connects to local db
query = 'SELECT * FROM rank'
df = read_sql_query(db, query)
df['Date'] = pd.to_datetime(df['Date'])
current_year = df.Date.dt.year.max()
df['Date'] = df['Date'].dt.date
seasons = list(df['Season'].unique())

seasons.sort()
currentSeason = max(seasons)
seasons.append("All")
seasons_drop = map(str, seasons)  # convert values to string for dropdown

df = df[['Season','Date','TeamName','TeamID','my_rank']]
hiddenCols = ['Date', 'Season', 'TeamID']
# removes hidden cols from df
columns = [x for x in list(df) if x not in hiddenCols]
#columns = list(df)
#print(list(df))
######################## rank Layout ########################
layout_rank = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["Rank Rating"], style={'marginTop': 15})
                ])
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='season-dropdown',
                        options=[{"label": i, "value": i}
                                 for i in seasons_drop],
                        value=currentSeason
                    ),
                ])
            )
        ),
        # Date Picker
        dbc.Row(
            dbc.Col(
                html.Div([
                    #dcc.DatePickerRange(
                    #    id='rank-date-picker-single',
                    #    # with_portal=True,
                    #    min_date_allowed=df['Date'].min(),
                    #    max_date_allowed=df['Date'].max(),
                    #    initial_visible_month=dt(
                    #        current_year, df['Date'].max().month, 1),
                    #    start_date=df['Date'].max() - timedelta(1),
                    #    end_date=df['Date'].max(),
                    #),
                    dcc.DatePickerSingle(
                        id='rank-date-picker-single',
                        # with_portal=True,
                        min_date_allowed=df['Date'].min(),
                        max_date_allowed=df['Date'].max(),
                        initial_visible_month=dt(
                            current_year, df['Date'].max().month, 1),
                        date=df['Date'].max(),
                    ),
                ],)
            )
        ),

        #),s
        # First Data Table
        dcc.Loading(
            id='rank-table-loading',
            type="default",
            children=dbc.Row(
                dbc.Col(
                    html.Div([
                        dash_table.DataTable(
                            id='datatable-rank-rating',
                            columns=[{"name": i, "id": i, 'deletable': True}
                                     for i in columns],
                            editable=True,
                            fixed_columns={'headers': True, 'data': 1},
                            style_table={'maxWidth': '1500px'},
                            #style_table={'overflowX': 'scroll'},
                            row_selectable="multi",
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            row_deletable=True,
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': c},
                                    'textAlign': 'left'
                                } for c in ['Date', 'WLoc', 'WName', 'WScore', 'LName', 'LScore']
                            ],
                            selected_rows=[0],
                            page_action='native',
                            page_current=0,
                            page_size=10,
                        ),
                    ], className="dash-table"),
                    width={"size": 6, "offset": 3},)
            ),
        ),
        
        #dbc.Row([
        #    dbc.Col(
        #        dcc.Graph(id="rank-histogram"), width=3
        #    ),
        #],
        #    id='graph-row')
    ], className="subpage")
], className="page")

######################## Callbacks ########################
#Callback for table
#########################################################

#change in season changes date

@app.callback(Output('rank-date-picker-single', 'date'),
              [Input('season-dropdown', 'value')])
def update_date_on_season(value):
    if value == 'All':
        # sets current date to max so we can get each seasons averages in next callback
        date = df['Date'].max()
    else:
        value = int(value)
        filter_df = df[(df['Season'] == value)]
        date = filter_df['Date'].max()
    return date

# Date Picker Callback change filter and visible month for selection


@app.callback([Output('datatable-rank-rating', 'data'),
               Output('rank-date-picker-single', 'initial_visible_month')],
              [Input('rank-date-picker-single', 'date'),
               Input('season-dropdown', 'value')])
def update_rank_date_season(date, value):

    new_month = date
    if date is not None:
        date = dt.strptime(date, '%Y-%m-%d').date()
    if value == 'All':
        value = str(value)
        #return ending avg season stats for each season
        dfList = []
        for season in seasons:
            #print(season)
            if season == 'All':
                continue
            season = int(season)
            filter_df = df[(df['Season'] == season)]
            filter_df = filter_df[(filter_df['Date'] <= date)]
            # sort to get most recent for each ID
            filter_df.Date = pd.to_datetime(filter_df.Date)
            filter_df = filter_df.sort_values(by='Date')
            filter_df.drop_duplicates(
                subset=['TeamID'], keep='last', inplace=True)
            dfList.append(filter_df)
        filter_df = pd.concat(dfList)

    else:
        value = int(value)
        filter_df = df[(df['Season'] == value)]
        filter_df = filter_df[(filter_df['Date'] <= date)]
        # sort to get most recent for each ID
        filter_df.Date = pd.to_datetime(filter_df.Date)
        filter_df = filter_df.sort_values(by='Date')
        filter_df.drop_duplicates(subset=['TeamID'], keep='last', inplace=True)
    #get most recent Row for each ID given date filter
    #sort df by rank rating
    filter_df = filter_df.sort_values(by='my_rank')
    filter_dict = filter_df.to_dict("rows")
    #lol = filter_df.values.tolist()
    return filter_dict, new_month


#@app.callback(
#    Output("rank-histogram", "figure"),
#    [Input('datatable-rank-rating', 'data')])
def make_histogram(data):
    data = pd.DataFrame.from_dict(data, orient='columns')
    if data.empty:
        return None
    else:
        return px.histogram(data, x='my_rank', nbins=20, height=300)
    #print(type(data))



#Call back to create distribution graph for each stat
#@app.callback([Output('datatable-rank-rating', 'data'),
#               Output('rank-date-picker-single', 'initial_visible_month')],
#              [Input('datatable-rank-rating', 'data')])
#def create_histogram_stats(data):#takes df of multiple stats

#    return html.Div([single_histogram(val) for val in data.columns])

#def single_histogram(val): #takes pd series of stat values and makes histogram

#    return hist
