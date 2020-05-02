

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
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd
from components.functions import read_sql_query
from dash.dependencies import Input, Output

from app import app

####################### Read in data ############################
#read in 2020 by default, refresh for anything else
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker
db = 'ncaab'
#query = 'SELECT * FROM boxscores WHERE Season = ?'
#params = 2020
#df = read_sql_query(db, query, params)
query = 'SELECT * FROM boxscores'
df = read_sql_query(db, query)
df['Date'] = pd.to_datetime(df['Date'])
current_year = df.Date.dt.year.max()
df['Date'] = df['Date'].dt.date
columns_basic = list(df[['Date', 'WLoc', 'WName', 'LName', 'WScore', 'LScore', 'W_wins', 'W_losses', 'L_wins', 'L_losses', 'WPOM', 'LPOM', 'WAst', 'WBlk', 'WDR', 'WOR', 'WFGA', 'WFGM', 'WFGA2', 'WFGM2', 'WFGA3', 'WFGM3',
                            'WFTA', 'WFTM', 'WStl', 'WTO', 'LAst', 'LBlk', 'LDR', 'LOR', 'LFGA', 'LFGM', 'LFGA2', 'LFGM2', 'LFGA3', 'LFGM3', 'LFTA', 'LFTM', 'LStl', 'LTO']])
columns_advanced = list(
    df[['Date', 'WLoc', 'WName', 'LName', 'WScore', 'LScore', 'W_wins', 'W_losses', 'L_wins', 'L_losses', 'WPOM', 'LPOM', 'WAdjsos', 'Wast_rtio', 'Wblk_pct', 'Wdef_rtg', 'Wdrb_pct', 'Wefg_pct', 'Wfour', 'Wft_rate', 'Wie', 'Woff_rtg', 'Worb_pct', 'Wposs', 'Wreb_pct', 'Wshoot_eff', 'Wsos', 'Wstl_pct', 'Wto_poss', 'Wts_pct',  'LAdjsos', 'Last_rtio', 'Lblk_pct', 'Ldef_rtg', 'Ldrb_pct', 'Lefg_pct', 'Lfour', 'Lft_rate', 'Lie', 'Loff_rtg', 'Lorb_pct', 'Lposs', 'Lreb_pct', 'Lshoot_eff', 'Lsos', 'Lstl_pct', 'Lto_poss', 'Lts_pct']])
df = df[['Date', 'WLoc', 'WName', 'LName', 'WScore', 'LScore', 'W_wins', 'W_losses', 'L_wins', 'L_losses', 'WPOM', 'LPOM',  'WAst', 'WBlk', 'WDR', 'WOR', 'WFGA', 'WFGM', 'WFGA2', 'WFGM2', 'WFGA3', 'WFGM3',
         'WFTA', 'WFTM', 'WStl', 'WTO', 'LAst', 'LBlk', 'LDR', 'LOR', 'LFGA', 'LFGM', 'LFGA2', 'LFGM2', 'LFGA3', 'LFGM3', 'LFTA', 'LFTM', 'LStl', 'LTO', 'WAdjsos', 'Wast_rtio', 'Wblk_pct', 'Wdef_rtg', 'Wdrb_pct', 'Wefg_pct', 'Wfour', 'Wft_rate', 'Wie', 'Woff_rtg', 'Worb_pct', 'Wposs', 'Wreb_pct', 'Wshoot_eff', 'Wsos', 'Wstl_pct', 'Wto_poss', 'Wts_pct',  'LAdjsos', 'Last_rtio', 'Lblk_pct', 'Ldef_rtg', 'Ldrb_pct', 'Lefg_pct', 'Lfour', 'Lft_rate', 'Lie', 'Loff_rtg', 'Lorb_pct', 'Lposs', 'Lreb_pct', 'Lshoot_eff', 'Lsos', 'Lstl_pct', 'Lto_poss', 'Lts_pct']]
columns_both = list(df)

#print(df.Date.max())
#print(list(df))
######################## Boxscore Layout ########################
layout_boxscore = html.Div([

    #    print_button(),

    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["Boxscore Stats"], style={'marginTop': 15})
                ])
            )
        ),
        # Date Picker
        dbc.Row(
            dbc.Col(
                html.Div([
                    dcc.DatePickerSingle(
                        id='my-date-picker-single',
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
        dbc.Row(
            dbc.Col(
                html.Div([
                    dcc.RadioItems(
                        options=[
                            {'label': 'Basic Boxscore', 'value': 'Basic'},
                            {'label': 'Advanced Boxscore', 'value': 'Advanced'},
                            {'label': 'All Boxscore', 'value': 'Both'},
                        ], value='Both',
                        labelStyle={'display': 'inline-block', 'width': '10%'},
                        id='radio-button-condensed'
                    )
                ])
            )
        ),
        #),
        # First Data Table
        dcc.Loading(
            id='boxscore-table-loading',
            type="default",
            children=dbc.Row(
            dbc.Col(
                html.Div([
                    dash_table.DataTable(
                        id='datatable-boxscore',
                        columns=[{"name": i, "id": i, 'deletable': True}
                                for i in columns_both],
                        editable=True,
                        fixed_columns={'headers': True, 'data': 6},
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
                #dbc.Spinner(html.Div(id="loading-output")),#spinner for loading of table
                ], className="dash-table"),
            )
        )
        ),
        
        # GRAPHS
    ], className="subpage")
], className="page")

######################## Callbacks ########################
#Callback for table
#########################################################

#season picker
#reference ID, then specific property
#@app.callback(Output('my-date-picker', 'data'),
#              [Input('radio-button-season', 'value')])
#input has to match input value
#def update_boxscore_season(value):
#    filter_df = df[df.Season == value]
#    return filter_df
    #return will be sent to output id & property


# Date Picker Callback change table 1
@app.callback(Output('datatable-boxscore', 'data'),
              [Input('my-date-picker-single', 'date')])
def update_boxscore_date(date):
    if date is not None:
        date = dt.strptime(date, '%Y-%m-%d').date()
    filter_df = df[(df['Date'] == date)]
    filter_dict = filter_df.to_dict("rows")
    #lol = filter_df.values.tolist()
    return filter_dict

#has loading circle while waiting for filter
#@app.callback(
#    Output("loading-output",
#           "children"), [Input("my-date-picker-single", "date")]
#)
#def load_output(n):
#    return None


# Callback and update data table columns
@app.callback(Output('datatable-boxscore', 'columns'),
              [Input('radio-button-condensed', 'value')])
def update_columns(value):
    if value == 'Basic':
    	column_set = [{"name": i, "id": i, 'deletable': True} for i in columns_basic]
    elif value == 'Advanced':
        column_set = [{"name": i, "id": i, "deletable": True} for i in columns_advanced]
    elif value == 'Both':
        column_set = [{"name": i, "id": i, "deletable": True}
                      for i in columns_both]
    return column_set




####################CODE NOT USED ###############################
def button(val):
    #dbc.Button("Block button", color="primary", block=True)
    #print(val)
    valID = val[2].replace(" ", "")
    valID = valID.replace("'", "")
    valID = valID.replace("&", "")
    valOut = val[4]
    #print(valID)
    #print(valOut)
    #print(1, val)
    button = dbc.Button(valID, id='button-{}'.format(valID), block=True)
    popover = dbc.Popover(
        [
            #popoverheaderbody(row) for row in listOfSeries
            dbc.PopoverHeader("Popover header"),
            dbc.PopoverBody(
                valOut
            ),
        ],
        id='popout-{}'.format(valID),
        is_open=False,
        target='button-{}'.format(valID)
    )
    return button


#@app.callback(Output('popovers', 'children'), [Input('my-date-picker', 'start_date'),
#                                              Input('my-date-picker', 'end_date')])
def popovers(start_date, end_date):
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d').date()
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%d').date()
    filter_df = df[(df['Date'] >= start_date) & (
        df['Date'] <= end_date)].copy()
    filter_df.WScore = filter_df.WScore.apply(str)
    filter_df.LScore = filter_df.LScore.apply(str)
    #matchup = filter_df.WName + "  vs.  "+filter_df.LName + "  |  " + \
    #    filter_df.WScore + " to " + filter_df.LScore
    lol = filter_df.values.tolist()
    return html.Div([popover(val) for val in lol])
    #return html.Div([button(val) for val in matchup])


def popover(val):
    #dbc.Button("Block button", color="primary", block=True)
    #print(val)
    valID = val[2].replace(" ", "")
    valID = valID.replace("'", "")
    valID = valID.replace("&", "")
    valOut = val[4]
    #print(valID)
    #print(valOut)
    #print(1, val)
    popover = dbc.Popover(
        [
            #popoverheaderbody(row) for row in listOfSeries
            dbc.PopoverHeader("Popover header"),
            dbc.PopoverBody(
                valOut
            ),
        ],
        id='popout-{}'.format(valID),
        is_open=False,
        target='button-{}'.format(valID)
    )
    return popover

#Date range callbacks
#updates date if change season
#@app.callback([Output('avg-stats-date-picker-single', 'start_date'),
#               Output('avg-stats-date-picker-single', 'end_date')],
#              [Input('season-dropdown', 'value')])
def update_date_on_season(value):
    value = int(value)
    filter_df = df[(df['Season'] == value)]
    date1 = filter_df['Date'].max() - timedelta(1)
    date2 = filter_df['Date'].max()
    return date1, date2

# Date Picker Callback change table 1


#@app.callback([Output('datatable-average-stats', 'data'),
#               Output('avg-stats-date-picker-single', 'initial_visible_month')],
#              [Input('avg-stats-date-picker-single', 'start_date'),
#               Input('avg-stats-date-picker-single', 'end_date'),
#               Input('season-dropdown', 'value')])
def update_average_stats_date_season(start_date, end_date, value):

    new_month = end_date
    if start_date is not None:
        start_date = dt.strptime(start_date, '%Y-%m-%d').date()
    if end_date is not None:
        end_date = dt.strptime(end_date, '%Y-%m-%d').date()

    if value == 'All':
        filter_df = df[(df['Date'] >= start_date) & (
            df['Date'] <= end_date)]
    else:
        value = int(value)
        filter_df = df[(df['Season'] == value)]
        filter_df = filter_df[(filter_df['Date'] >= start_date) & (
            filter_df['Date'] <= end_date)]
    filter_dict = filter_df.to_dict("rows")
    #lol = filter_df.values.tolist()
    return filter_dict, new_month


