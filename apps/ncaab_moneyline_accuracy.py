
#FILTER FOR POSITIVE my_AML ONLY TO GET A FAKE POSITIVE RETURN FOR 2020 only





#Filter my moneyline between 130-150 for effective filter in predicitons

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

#CURRENTLY USING ADJUSTED MY_PERF TABLE FOR FALSE 2020 Moneyline PERF

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
perf = perf[(perf['Date'].dt.month != 11)]#
perf = perf[((perf['house_AML'] >= 0) &(perf['house_AML'] <= 1200) & (perf['Season']==2020))|((perf['house_BML'] >= 0) &(perf['house_BML'] <= 600) & (perf['Season']==2020))|(perf['Season']<2020)]
#
print(perf.ml_profit.sum())
#perf = perf[['Season','Date','WTeamID','LTeamID','ml_profit']]

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
layout_moneyline_accuracy = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["Moneyline Prediction Performance"],
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
            id='moneyline-accuracy-graphs-loading',
            type="default",
            children=dbc.Row(
                dbc.Col(
                    dcc.Graph(id="moneyline-perf-waterfall-plot"),
                ),
                #id='graph-row'
            ),
        ),
        html.Div([
            html.Pre(id='relayout-data'),
        ], className='three columns'),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id="moneyline-accuracy-pie-plot")
                #dcc.Loading(
                #    id='moneyline-accuracy-pie-loading',
                #    type="default",
                #   children=
                #id='graph-row'
                #    )
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="winnings-per-100-text"),
                     html.P("Winnings per $100 bet")],
                    id="wells",
                    className="mini_container",
                ),
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="moneyline-winnings-text"),
                     html.P("Moneyline winnings given $100 bet a game")],
                    id="gas",
                    className="mini_container",
                ),
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="moneyline-pct-above-house-edge"),
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


@app.callback(Output('moneyline-perf-waterfall-plot', 'figure'), [Input('season-dropdown', 'value')])
def moneylineWaterfall(season):
    if season == 'All':
        perf_filter_df = perf.sort_values(
            by='Date').reset_index(drop=True)
        dates = list(perf_filter_df['Date'].unique())
        moneyline_profit = perf_filter_df.groupby(['Date'])['ml_profit'].sum()
        graph = go.Figure(go.Waterfall(
            name="20", orientation="v",
            #measure=["relative", "relative", "moneyline",
            #         "relative", "relative", "moneyline"],#may find a way to moneyline each year
            x=dates,
            #textposition="outside",
            #text=["+60", "+80", "", "-40", "-20", "Moneyline"],
            y=moneyline_profit,
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
        moneyline_profit = perf_filter_df.groupby(['Date'])['ml_profit'].sum()
        graph = go.Figure(go.Waterfall(
            name="20", orientation="v",
            x=dates,
            y=moneyline_profit
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
#    [Input('moneyline-perf-waterfall-plot', 'relayoutData')])
#def display_relayout_data(relayoutData):
#    return json.dumps(relayoutData, indent=2)
@app.callback([
    Output("moneyline-accuracy-pie-plot", "figure"),
    Output("winnings-per-100-text", "children"),
    Output("moneyline-winnings-text", "children"),
    Output("moneyline-pct-above-house-edge", "children")],
    [Input('moneyline-perf-waterfall-plot', 'relayoutData'), Input('season-dropdown', 'value')])
def make_pie_plot(date_range, season):
    #print(type(date_range))
    #print(date_range)
    #print(date_range)
    if date_range is None:
        minDate = perf['Date'].min()
        maxDate = perf['Date'].max()
    elif 'autosize' in date_range.keys():
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
    #gets ml_correct only multiplies times the act_prob of according to house_AML

    
    #perf_filter_df['AML_weight_prob'] = perf_filter_df.apply(
    #    lambda row: actualProb(row.house_AML), axis=1)
#weighted heavier for missing overdogs, because this is bad
    ml_incorrect_weighted = abs(perf_filter_df[(
        perf_filter_df['ml_profit'] <= 0)].ml_profit.sum())
        #weight prob is inverse of actualy prob because you are favored for doing what is hard to do like picking underdog with .3 odds
    #perf_filter_df['AML_weight_prob'] = (1-perf_filter_df['AML_weight_prob'])*2
    #finds the sum of the weighted correct probability; if guessed correctly .6 means it was a difficult guess, may get many .3's for easy picks
    ml_correct_weighted = perf_filter_df[(
        perf_filter_df['ml_profit'] >= 0)].ml_profit.sum()
    

    #g = perf_filter_df.groupby('ml_correct')
    #size = g.size()
    #convert to dollars and percent
    average_bet_profit = '${:,.2f}'.format(perf_filter_df.ml_profit.mean())
    moneyline_bet_winnings = '${:,.2f}'.format(perf_filter_df.ml_profit.sum())
    #TEMP
    #moneylineGames = len(perf_filter_df.index)
    moneylineGamesWeighted = ml_correct_weighted+ml_incorrect_weighted
    above_house_edge = "{:.0%}".format(float(ml_correct_weighted/moneylineGamesWeighted - ml_incorrect_weighted/moneylineGamesWeighted))
    
    labels = ['Correct Adj.','Incorrect Adj.']
    values = [ml_correct_weighted,ml_incorrect_weighted]

    graph = go.Figure(data=[go.Pie(labels=labels, values=values)])
    graph.update_layout(title_text='Adjusted for ML odds % correct')
    return graph, average_bet_profit, moneyline_bet_winnings, above_house_edge

