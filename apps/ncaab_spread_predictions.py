

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
odds = odds[['Season','Date', 'ATeamID', 'BTeamID', 'A_Spread']]
currentSeason = odds['Season'].max()
#SELECT ONLY 2020 for now due to number of rows
query = 'SELECT * FROM my_pred WHERE Season = ?'
params = currentSeason
pred = read_sql_query(db, query, params)#
#pred = pd.read_csv("data/my_pred_2020.csv")
#pred['Date'] = pd.to_datetime(pred['Date'])
pred = pred[['Season','Date','Time','ATeamID','BTeamID','TeamA','TeamB', 'Spread Line', 'Spread Win Prob A','Spread Win Prob B', 'Spread Pick']]
#

tempDF1 = odds.merge(pred, how='inner', left_on=[
    'Date', 'ATeamID', 'BTeamID'], right_on=['Date', 'ATeamID', 'BTeamID'])
tempDF2 = odds.merge(pred, how='inner', left_on=[
    'Date', 'BTeamID', 'ATeamID'], right_on=['Date', 'ATeamID', 'BTeamID'])

tempDF1 = tempDF1[['Season_y','Date', 'ATeamID', 'BTeamID', 'TeamA', 'TeamB', 'A_Spread',
                   'Spread Line', 'Spread Win Prob A', 'Spread Win Prob B', 'Spread Pick']]
tempDF1.columns = ['Season','Date', 'ATeamID', 'BTeamID', 'TeamA', 'TeamB', 'house_Spread_Line',
                   'Spread Line',  'Spread Win Prob A', 'Spread Win Prob B', 'Spread Pick']

tempDF2['A_Spread'] = -tempDF2['A_Spread']
tempDF2 = tempDF2[['Season_y', 'Date', 'ATeamID_y', 'BTeamID_y', 'TeamA', 'TeamB', 'A_Spread',
                   'Spread Line', 'Spread Win Prob A', 'Spread Win Prob B', 'Spread Pick']]
tempDF2.columns = ['Season','Date', 'ATeamID', 'BTeamID', 'TeamA', 'TeamB', 'house_Spread_Line',
                   'Spread Line',  'Spread Win Prob A', 'Spread Win Prob B', 'Spread Pick']

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
layout_spread_predictions = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["Spread Predictions"], style={'marginTop': 15})
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
                        id='spread-predictions-date-picker-single',
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
            id = 'spread-predictions-graph-loading',
            type = "default",
            children=dbc.Row([
                dbc.Col([
                    html.Div(id='spread-prediction-graphs')
                ]),
            ])
        ),
        
    ], className="subpage")
], className="page")

######################## Callbacks ########################
#Callback for table
#########################################################

#scatter plots of each rank and it's correlation to win%


@app.callback(Output('spread-prediction-graphs', 'children'), [Input('spread-predictions-date-picker-single', 'date')])

def create_spread_prediction_graphs(date):
    
    print(date)
    if date is not None:
        date = dt.strptime(date, '%Y-%m-%d').date()
    prob_table = pred[(pred['Date'] == date)]

    prob_table['Spread Prob'] = prob_table['Spread Win Prob A'].round(3)
    #convert spread prob so selecting B is above .5
    prob_table['Spread Prob'] = np.where(
        prob_table['Spread Prob'] < .5, .5+abs(prob_table['Spread Prob']-.5), prob_table['Spread Prob'])
    
    spreadDict = {}
    rows = []
    count = 0
    for name, group in prob_table.groupby(['TeamA', 'TeamB'], sort=False):
        # Build dataframe
        #print(name)
        game = pd.DataFrame()
        game['Spread Line'] = group['Spread Line']
        game['Expected Win %'] = group['Spread Prob']
        game['Spread Pick'] = group['Spread Pick']
        group['Spread Line'] = group['TeamA'] + \
            " ("+group['Spread Line'].map(str)+")"
        #winner = group[['Spread Pick', 'Spread Line']].values.tolist()
        #get line with mi
        minLine = game[game['Expected Win %'] == (
            game['Expected Win %'].min())]['Spread Line'].values[0]
        color = np.array(['rgb(  0,  0,  0)']*game['Spread Line'].shape[0])
        color[game['Spread Line'] > minLine] = 'rgb(130,0,0)'
        color[game['Spread Line'] < minLine] = 'rgb(204,204,2)'

        title = name[0] + " vs. " + name[1]#

        #name x axis after TeamA
        game.rename(columns={'Spread Line': name[0]+' Line'}, inplace=True)

        #color = color.tolist()
        bar_graph = px.bar(game, x=name[0]+' Line',
                           y='Expected Win %',  range_y=[.4, .7], title=title, color = "Spread Pick")
        bar_graph.add_trace(
            go.Scatter(
                x = [i for i in range(-35,10,1)],
                y = [.524 for i in range(-35,10,1)],
                mode='lines',
                showlegend=False,
                textposition = "top center",
                hovertemplate="House edge given -110 vig<extra></extra>",
                opacity=.5,
                marker_color='rgba(224, 123, 57, .8)'
        ))
        spreadDict.update({name: bar_graph})
        count += 1
        if count%3 == 0:#every 3 graphs add to rows as dict "row" 
            rows.append(spreadDict)
            #print(spreadDict)
            spreadDict = {}
        
        #spreadList.append(bar_graph)
    #print(bool(spreadDict))
    if bool(spreadDict):#append dict if any cols left over, i.e. 1 or 2 graphs
        rows.append(spreadDict)
    #return html.Div([graph(val) for val in selected])


    #for row in rows of dict graphs grouped in 3's - create row
    #print(len(rows))
    #is_loading = False
    return html.Div([row(rowDict) for rowDict in rows])


def row(spreadDict):
    # for graph in dict graph grouped in 3's create col/graph
    #print(spreadDict)
    return dbc.Row([graph(game, spreadDict[game]) for game in spreadDict])

def graph(name, graph):
    return dbc.Col(dcc.Graph(id='graph-{}'.format(name), figure=graph))
#def graph(name, graph):
    
