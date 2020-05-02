

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
import time

from app import app

####################### Read in data ############################
#read in 2020 by default, refresh for anything else
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker
db = 'ncaab'#connects to local db
query = 'SELECT * FROM inSeasonAverages'
params = 2020
df = read_sql_query(db, query)
query = 'SELECT * FROM team'
team = read_sql_query(db, query)
team = team[['TeamID','TeamName']]
df = df.merge(team, how='inner', left_on=[
    'TeamID'], right_on=['TeamID'])

df['Date'] = pd.to_datetime(df['Date'])
current_year = df.Date.dt.year.max()
df['Date'] = df['Date'].dt.date
seasons = list(df['Season'].unique())
currentSeason = max(seasons)
seasons.append("All")
seasons_drop = map(str, seasons)#convert values to string for dropdown

df = df[['Season','Date','TeamName','TeamID', 'win_pct', 'n_wins','n_loss', 'mov', 'score_op', 'off_rtg', 'def_rtg', 'sos', 'Adjsos', 'ie', 'four', 'shoot_eff', 'ts_pct', 'efg_pct', '3pta_pct', 'ft_rate', 'ast_rtio', 'blk_pct', 'reb_pct', 'orb_pct', 'drb_pct', 'stl_pct', 'to_poss', 'wins_top25', 'wins_top5']]
hiddenCols = ['Date','Season','TeamID']
columns = [x for x in list(df) if x not in hiddenCols]#removes hidden cols from df
stats_cols = ['win_pct', 'n_wins', 'n_loss', 'mov', 'score_op', 'off_rtg', 'def_rtg', 'sos', 'Adjsos', 'ie', 'four', 'shoot_eff', 'ts_pct',
              'efg_pct', '3pta_pct', 'ft_rate', 'ast_rtio', 'blk_pct', 'reb_pct', 'orb_pct', 'drb_pct', 'stl_pct', 'to_poss', 'wins_top25', 'wins_top5']
#columns = list(df)
#print(list(df))
######################## Average Stats Layout ########################
layout_average_stats = html.Div([

    #    print_button(),

    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["Average Stats"], style={'marginTop': 15})
                ])
            )
        ), 
        dbc.Row(
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='season-dropdown',
                        options=[{"label":i,"value": i}
                                    for i in seasons_drop],
                        value=currentSeason
                    ),
                ])
             )
        ) ,
        # Date Picker
        dbc.Row(
            dbc.Col(
                html.Div([
                    #dcc.DatePickerRange(
                    #    id='avg-stats-date-picker-single',
                    #    # with_portal=True,
                    #    min_date_allowed=df['Date'].min(),
                    #    max_date_allowed=df['Date'].max(),
                    #    initial_visible_month=dt(
                    #        current_year, df['Date'].max().month, 1),
                    #    start_date=df['Date'].max() - timedelta(1),
                    #    end_date=df['Date'].max(),
                    #),
                    dcc.DatePickerSingle(
                        id='avg-stats-date-picker-single',
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
        
        #),
        # First Data Table
        dcc.Loading(
            id='spread-predictions-graph-loading',
            type="default",
            children=dbc.Row(
                dbc.Col(
                    html.Div([
                        dash_table.DataTable(
                            id='datatable-average-stats',
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
                )
            ),
        ),
        
        dbc.Row([
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='stats-dropdown',
                        options=[{"label": i, "value": i}
                                for i in stats_cols],
                        value=stats_cols[0]
                    ),
                ])
            ),
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='stats-dropdown-x',
                        options=[{"label": i, "value": i}
                                for i in stats_cols],
                        value=stats_cols[0]
                    ),
                ])),
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='stats-dropdown-y',
                        options=[{"label": i, "value": i}
                                for i in stats_cols],
                        value=stats_cols[0]
                    ),
                ])
            ),
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    id='average-stats-histogram-loading',
                    type="default",
                    children=dcc.Graph(id="stats-histogram")
                ),
            width=3),
            dbc.Col(
                dcc.Loading(
                    id='average-stats-histogram-loading',
                    type="default",
                    children=dcc.Graph(id="stats-scatter-plot")
                ),
            ),
                
        ],  id='graph-row')
        
    ], className="subpage")
], className="page")

######################## Callbacks ########################
#Callback for table
#########################################################

#change in season changes date
@app.callback(Output('avg-stats-date-picker-single', 'date'),
               [Input('season-dropdown', 'value')])

def update_date_on_season(value):
    if value == 'All':
        date = df['Date'].max() #sets current date to max so we can get each seasons averages in next callback
    else:
        value = int(value)
        filter_df = df[(df['Season'] == value)]
        date = filter_df['Date'].max()
    return date

# Date Picker Callback change filter and visible month for selection


@app.callback([Output('datatable-average-stats', 'data'), 
               Output('avg-stats-date-picker-single', 'initial_visible_month')],
              [Input('avg-stats-date-picker-single', 'date'),
               Input('season-dropdown', 'value')])
def update_average_stats_date_season(date, value):
    
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
            filter_df.Date = pd.to_datetime(filter_df.Date)#sort to get most recent for each ID
            filter_df = filter_df.sort_values(by='Date')
            filter_df.drop_duplicates(subset=['TeamID'], keep='last', inplace=True)
            dfList.append(filter_df)
        filter_df = pd.concat(dfList)
    
    else:
        value = int(value)
        filter_df = df[(df['Season'] == value)]
        filter_df = filter_df[(filter_df['Date'] <= date)]
        filter_df.Date = pd.to_datetime(filter_df.Date)#sort to get most recent for each ID
        filter_df = filter_df.sort_values(by='Date')
        filter_df.drop_duplicates(subset=['TeamID'], keep='last', inplace=True)
    #get most recent Row for each ID given date filter
    print('output table',filter_df.shape)
    filter_dict = filter_df.to_dict("rows")
    print(len(filter_dict))
    #lol = filter_df.values.tolist()
    return filter_dict, new_month


@app.callback(
    Output("stats-histogram", "figure"),
    [Input('datatable-average-stats', 'data'), Input("stats-dropdown", "value")])

def make_histogram(data,value):
    #time.sleep(5)
    if data is None:
        return None
    data_hist = pd.DataFrame.from_dict(data, orient='columns')
    print('hist',data_hist.shape)
    #if data_hist.empty:
    #    return None
    #else:
    return px.histogram(data_hist, x=value, nbins=20, height=300)
    #print(type(data))
    


@app.callback(
    Output("stats-scatter-plot", "figure"),
    [Input('datatable-average-stats', 'data'), Input("stats-dropdown-x", "value"), Input("stats-dropdown-y", "value")])
def make_scatter_plot(data, value_x, value_y):
    #time.sleep(5)
    if data is None:
        return None
    data_scatter = pd.DataFrame.from_dict(data, orient='columns')
    #if data_scatter.empty:
    #    return None
    #else:
    print('scat',data_scatter.shape)
    return px.scatter(data_scatter, x=value_x, y=value_y, hover_name="TeamName", height=300)
#Call back to create distribution graph for each stat
#@app.callback([Output('datatable-average-stats', 'data'),
#               Output('avg-stats-date-picker-single', 'initial_visible_month')],
#              [Input('datatable-average-stats', 'data')])
#def create_histogram_stats(data):#takes df of multiple stats

#    return html.Div([single_histogram(val) for val in data.columns])

#def single_histogram(val): #takes pd series of stat values and makes histogram

#    return hist
