

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
from dash.dependencies import Input, Output

from app import app

####################### Read in data ############################
#read in 2020 by default, refresh for anything else
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker
db = 'ncaab'  # connects to local db
query = 'SELECT * FROM odds'
odds = read_sql_query(db, query)
odds = odds[['Season', 'Date', 'ATeamID', 'BTeamID', 'AML', 'BML']]
currentSeason = odds['Season'].max()
query = 'SELECT * FROM my_pred WHERE Season = ?'
params = currentSeason
pred = read_sql_query(db, query, params)
#pred = pd.read_csv("data/my_pred_2020.csv")
#pred['Date'] = pd.to_datetime(pred['Date'])
pred = pred[['Season', 'Date', 'Time', 'ATeamID', 'BTeamID', 'TeamA', 'TeamB',
             'AML','BML', 'ML EV A', 'ML EV B', 'ML Pick A','ML Pick B']]


tempDF1 = odds.merge(pred, how='inner', left_on=[
    'Date', 'ATeamID', 'BTeamID'], right_on=['Date', 'ATeamID', 'BTeamID'])
tempDF2 = odds.merge(pred, how='inner', left_on=[
    'Date', 'BTeamID', 'ATeamID'], right_on=['Date', 'ATeamID', 'BTeamID'])

tempDF1 = tempDF1[['Season_y', 'Date', 'ATeamID', 'BTeamID', 'TeamA', 'TeamB', 'AML_x','BML_x', 'AML_y','BML_y',
                     'ML EV A', 'ML EV B', 'ML Pick A','ML Pick B']]
tempDF1.columns = ['Season', 'Date', 'ATeamID', 'BTeamID', 'TeamA', 'TeamB', 'house_AML', 'house_BML', 'my_AML', 'my_BML',
                     'ML EV A', 'ML EV B', 'ML Pick A', 'ML Pick B']

tempDF2 = tempDF2[['Season_y', 'Date', 'ATeamID_y', 'BTeamID_y', 'TeamA', 'TeamB', 'BML_x', 'AML_x',  'AML_y', 'BML_y',
                    'ML EV A', 'ML EV B', 'ML Pick A', 'ML Pick B']]
tempDF2.columns = ['Season', 'Date', 'ATeamID', 'BTeamID', 'TeamA', 'TeamB', 'house_AML', 'house_BML', 'my_AML', 'my_BML',
                  'ML EV A', 'ML EV B', 'ML Pick A', 'ML Pick B']

frames = [tempDF1, tempDF2]
pred = pd.concat(frames).reset_index(drop=True)
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker



pred['Date'] = pd.to_datetime(pred['Date'])
current_year = pred.Date.dt.year.max()
pred['Date'] = pred['Date'].dt.date
seasons = list(pred['Season'].unique())
seasons.sort()
currentSeason = max(seasons)
seasons.append("All")
seasons_drop = map(str, seasons)  # convert values to string for dropdown


######################## RANK Layout ########################
layout_moneyline_predictions = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["ML Predictions"], style={'marginTop': 15})
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
                    dcc.DatePickerSingle(
                        id='moneyline-predictions-date-picker-single',
                        # with_portal=True,
                        min_date_allowed=pred['Date'].min(),
                        max_date_allowed=pred['Date'].max(),
                        initial_visible_month=dt(
                            current_year, pred['Date'].max().month, 1),
                        date=pred['Date'].max(),
                    ),
                ],)
            )
        ),
        dcc.Loading(
            id='moneyline-predictions-graph-loading',
            type="default",
            children=dbc.Row([
                dbc.Col([
                    html.Div(id='moneyline-prediction-graphs')
                ]),
            ])
        ),

    ], className="subpage")
], className="page")

######################## Callbacks ########################
#Callback for table
#########################################################

#scatter plots of each rank and it's correlation to win%


@app.callback(Output('moneyline-prediction-graphs', 'children'), [Input('moneyline-predictions-date-picker-single', 'date')])
def create_moneyline_prediction_graphs(date):

    print(date)
    if date is not None:
        date = dt.strptime(date, '%Y-%m-%d').date()
    prob_table = pred[(pred['Date'] == date)]

    moneylineDict = {}
    rows = []
    count = 0
    for name, group in prob_table.groupby(['TeamA', 'TeamB'], sort=False):
        # Build dataframe
        #print(name)
        group = group[(group['my_AML'] <= 600)&(group['my_AML'] >= -600)]
        gameA = group[(group['ML EV A'] >= 0)]  # doesn't show negative ML
        gameB = group[(group['ML EV B'] >= 0)]#
        #game['my_AML'] = group['my_AML']
        gameA['Expected Value A'] = gameA['ML EV A']
        #game['my_BML'] = group['my_BML']
        gameB['Expected Value B'] = gameB['ML EV B']
        #game['my_AML'] = game['TeamA'] + \
        #    " Line: ("+game['my_AML'].map(str)+")"
        gameA['ML EV A'] = "Exp. Val.: "+gameA['ML EV A'].map(str)
        gameB['ML EV B'] = "Exp. Val.: "+gameB['ML EV B'].map(str)
        hoverA = gameA[['my_AML', 'ML EV A']].values.tolist()
        hoverB = gameB[['my_BML', 'ML EV B']].values.tolist()
        #game['ML Pick A'] = game['ML Pick A']
        #game['ML Pick B'] = game['ML Pick B']
        #group['ML Line'] = group['TeamA'] + \
        #    " ("+group['ML Line'].map(str)+")"
        #winner = group[['ML Pick', 'ML Line']].values.tolist()
        #get line with mi

        title = name[0] + " vs. " + name[1]

        #name x axis after TeamA
        #game.rename(columns={'ML Line': name[0]+' Line'}, inplace=True)#
        width = [25]*45
        #color = color.tolist()
        bar_graph = go.Figure()
        if gameA['Expected Value A'].mean()>gameB['Expected Value B'].mean():#adds the larger graph first so you can seel all bars
            bar_graph.add_trace(go.Bar(
                x=gameA['my_AML'],
                y=gameA['Expected Value A'],
                text=gameA['my_AML'],
                hoverlabel={'align':"auto"},
                hovertext=hoverA,
                hoverinfo="text",
                width=width,
                name=name[0]
                ))
            bar_graph.add_trace(go.Bar(
                x=gameB['my_BML'], 
                y=gameB['Expected Value B'],#
                text=gameB['my_BML'],
                hoverlabel={'align':"auto"},
                hovertext=hoverB,
                hoverinfo="text",
                width=width,
                name=name[1]#
                ))
        else:
            bar_graph.add_trace(go.Bar(
                x=gameB['my_BML'],
                y=gameB['Expected Value B'],
                text=gameB['my_BML'],
                hoverlabel={'align': "auto"},
                hovertext=hoverB,
                hoverinfo="text",
                width=width,
                name=name[1]
            ))
            bar_graph.add_trace(go.Bar(
                x=gameA['my_AML'],
                y=gameA['Expected Value A'],
                text=gameA['my_AML'],
                hoverlabel={'align': "auto"},
                hovertext=hoverA,
                hoverinfo="text",
                width=width,
                name=name[0]
            ))
        
        bar_graph.update_layout(title=title,
                          xaxis_title='ML',
                          yaxis_title='Expected Value')
        moneylineDict.update({name: bar_graph})
        count += 1
        if count % 3 == 0:  # every 3 graphs add to rows as dict "row"
            rows.append(moneylineDict)
            #print(moneylineDict)
            moneylineDict = {}

        #moneylineList.append(bar_graph)
    #print(bool(moneylineDict))
    if bool(moneylineDict):  # append dict if any cols left over, i.e. 1 or 2 graphs
        rows.append(moneylineDict)
    #return html.Div([graph(val) for val in selected])

    #for row in rows of dict graphs grouped in 3's - create row
    #print(len(rows))
    #is_loading = False
    return html.Div([row(rowDict) for rowDict in rows])


def row(moneylineDict):
    # for graph in dict graph grouped in 3's create col/graph
    #print(moneylineDict)
    return dbc.Row([graph(game, moneylineDict[game]) for game in moneylineDict])


def graph(name, graph):
    return dbc.Col(dcc.Graph(id='graph-{}'.format(name), figure=graph))
#def graph(name, graph):
