



#Filter my total between 130-150 for effective filter in predicitons

#Read in query with SQL, but do advanced manipulation in memory with Pandas


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

#CURRENTLY USING ADJUSTED MY_PERF TABLE FOR FALSE 2020 Total PERF

####################### Read in data ############################
#read in 2020 by default, refresh for anything else
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker
db = 'ncaab'  # connects to local db
query = 'SELECT * FROM my_perf'
perf = read_sql_query(db, query)
query = 'SELECT * FROM boxscores'
box = read_sql_query(db, query)
box = box[['Date', 'WTeamID', 'LTeamID', 'WLoc']]
perf = perf.merge(box, how='inner', left_on=[
    'Date', 'WTeamID', 'LTeamID'], right_on=['Date', 'WTeamID', 'LTeamID'])
#perf = perf[(perf['Season'] == 2020)]
print(perf.shape)
perf.drop_duplicates(
    subset=['WTeamID', 'LTeamID', 'Date'], keep=False, inplace=True)
#test filtering rules for performance

perf = perf[(perf['Season'] >= 2015)]
perf = perf[(perf['Date'].dt.month != 11)]
perf = perf[((perf['my_Total_Line'] >= 130) & (
perf['my_Total_Line'] <= 150)& (perf['Season']==2020))|(perf['Season']<2020)]  #filter on 130-150 only on season 2020
#perf = perf[(perf['my_Total_Line'] >= 120) & (
#    perf['my_Total_Line'] <= 160)]#7473, -3671
#perf = perf[(perf['my_Total_Line'] < 120) | (
#    perf['my_Total_Line'] > 160)]#3449, 22186; neg 2020
#no line filter 13960, 16374
#perf = perf[(perf['WLoc'] != 'N')]#12766, 19009
#perf['line_diff'] = abs(perf['my_Total_Line']-perf['house_Total_Line'])
#perf = perf[(perf['line_diff'] >= 14)]#4,11889, 20631
#6, 10750,27223
#8, 9631, 23516
#10, 8565, 24931
#14, 6533, 29534 #best for 2020 and other years?
#17, 5228, 27829
print(perf.total_profit.sum())
print(perf.shape)
#perf = perf[['Season','Date','WTeamID','LTeamID','total_profit']]

#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker


perf['Date'] = pd.to_datetime(perf['Date'])
current_year = perf.Date.dt.year.max()
perf['Date'] = perf['Date'].dt.date
seasons = list(perf['Season'].unique())
seasonsList = seasons
seasons.sort()
currentSeason = max(seasons)
seasons.append("All")
seasons_drop = map(str, seasons)  # convert values to string for dropdown


######################## RANK Layout ########################
layout_total_accuracy = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["Total Prediction Performance"],
                            style={'marginTop': 15})
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
        #Add date slicer
        dcc.Loading(
            id='total-accuracy-graphs-loading',
            type="default",
            children=dbc.Row(
                dbc.Col(
                    dcc.Graph(id="total-perf-waterfall-plot"),
                ),
                #id='graph-row'
            ),
        ),
        html.Div([
            html.Pre(id='relayout-data'),
        ], className='three columns'),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id="total-accuracy-pie-plot")
                #dcc.Loading(
                #    id='total-accuracy-pie-loading',
                #    type="default",
                #   children=
                #id='graph-row'
                #    )
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="total-winnings-per-100-text"),
                     html.P("Winnings per $100 bet")],
                    id="wells",
                    className="mini_container",
                ),
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="total-total-winnings-text"),
                     html.P("Total winnings given $100 bet a game")],
                    id="gas",
                    className="mini_container",
                ),
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="total-pct-above-house-edge"),
                     html.P("Margin between correct & incorrect picks")],
                    id="oil",
                    className="mini_container",
                ),
            )



        ]),
    ], className="subpage")
], className="page")

######################## Callbacks ########################
#Callback for table
#########################################################

#callback for content around 2020 explanation




#scatter plots of each rank and it's correlation to win%


@app.callback(Output('total-perf-waterfall-plot', 'figure'), [Input('season-dropdown', 'value')])
def totalWaterfall(season):
    if season == 'All':
        perf_filter_df = perf.sort_values(
            by='Date').reset_index(drop=True)
        dates = list(perf_filter_df['Date'].unique())
        total_profit = perf_filter_df.groupby(['Date'])['total_profit'].sum()
        graph = go.Figure(go.Waterfall(
            name="20", orientation="v",
            #measure=["relative", "relative", "total",
            #         "relative", "relative", "total"],#may find a way to total each year
            x=dates,
            #textposition="outside",
            #text=["+60", "+80", "", "-40", "-20", "Total"],
            y=total_profit,
            #connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        graph.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        return graph
    else:
        season = int(season)
        perf_filter_df = perf[(perf['Season'] == season)]
        perf_filter_df = perf_filter_df.sort_values(
            by='Date').reset_index(drop=True)
        dates = list(perf_filter_df['Date'].unique())
        total_profit = perf_filter_df.groupby(['Date'])['total_profit'].sum()
        graph = go.Figure(go.Waterfall(
            name="20", orientation="v",
            x=dates,
            y=total_profit
        ))
        graph.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        return graph


#@app.callback(
#    Output('relayout-data', 'children'),
#    [Input('total-perf-waterfall-plot', 'relayoutData')])
#def display_relayout_data(relayoutData):
#    return json.dumps(relayoutData, indent=2)
@app.callback([
    Output("total-accuracy-pie-plot", "figure"),
    Output("total-winnings-per-100-text", "children"),
    Output("total-total-winnings-text", "children"),
    Output("total-pct-above-house-edge", "children")],
    [Input('total-perf-waterfall-plot', 'relayoutData'), Input('season-dropdown', 'value')])
def make_pie_plot(date_range, season):
    #print(type(date_range))
    #print(date_range)
    if 'autosize' in date_range.keys():
        #print(1,date_range['autosize'])
        if season == 'All':
            minDate = perf['Date'].min()
            maxDate = perf['Date'].max()
        else:
            season = int(season)
            perf_filter_season_df = perf[(perf['Season'] == season)]
            minDate = perf_filter_season_df['Date'].min()
            maxDate = perf_filter_season_df['Date'].max()

    elif 'xaxis.range' in date_range.keys():

        #add logic to first remove any text beyond the YYYY-MM-DD
        strip_str_beg = date_range['xaxis.range'][0][0:10]
        strip_str_end = date_range['xaxis.range'][1][0:10]
        minDate = dt.strptime(strip_str_beg, '%Y-%m-%d').date()
        maxDate = dt.strptime(strip_str_end, '%Y-%m-%d').date()
        #2019-12-01 17: 17: 03.8532
        #.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
        #print(2,date_range['xaxis.range'][0])
        #print(type(date_range['xaxis.range'][0]))
        #print(3,date_range['xaxis.range'][1])
    else:
        print("Error")
        print(date_range)
    #parse date range into beg and endDate
    #filter df
    perf_filter_df = perf[(perf['Date'] <= maxDate) &
                          (perf['Date'] >= minDate)]
    #perf_table = perf[(perf['Date'] == date)]
    g = perf_filter_df.groupby('total_correct')
    size = g.size()
    #convert to dollars and percent
    average_bet_profit = '${:,.2f}'.format(perf_filter_df.total_profit.mean())
    total_bet_winnings = '${:,.2f}'.format(perf_filter_df.total_profit.sum())
    #TEMP
    totalGames = len(perf_filter_df.index)
    above_house_edge = "{:.0%}".format(
        float(size.get(key=1))/totalGames-float(size.get(key=0))/totalGames)
    graph = px.pie(perf_filter_df, values=size, names=size.index, height=300, title='Over/Under % Correct')
    return graph, average_bet_profit, total_bet_winnings, above_house_edge
