

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
from dash.dependencies import Input, Output

from app import app

####################### Read in data ############################
#read in 2020 by default, refresh for anything else
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker
db = 'ncaab'  # connects to local db
query = 'SELECT * FROM rank'
rank = read_sql_query(db, query)

query = 'SELECT * FROM boxscores'
boxscores = read_sql_query(db, query)
boxscores = boxscores[['Season','LgameNum','WgameNum','LTeamID','WTeamID','roundDayNum']]

rank = rank[['Date','Season', 'TeamID', 'roundDayNum','my_rank', 'kp_rank','net_rank']]
#get all rankings on boxscore to compare accuracy
rank_join = rank.copy()
rank_join.dropna(subset=['my_rank', 'kp_rank',
                         'net_rank'], inplace=True)
boxscores = boxscores.merge(rank_join, how='left', left_on=[
              'Season', 'WTeamID', 'roundDayNum'], right_on=['Season', 'TeamID', 'roundDayNum'])

boxscores = boxscores.merge(rank_join, how='left', left_on=[
    'Season', 'LTeamID', 'roundDayNum'], right_on=['Season', 'TeamID', 'roundDayNum'])
boxscores.rename(columns={'kp_rank_x': 'Wkp_rank', 'kp_rank_y': 'Lkp_rank', 
                'my_rank_x': 'Wmy_rank', 'my_rank_y': 'Lmy_rank',
                'net_rank_x': 'Wnet_rank', 'net_rank_y': 'Lnet_rank'}, inplace=True)
boxscores['my_correct'] = None
boxscores['kp_correct'] = None
boxscores['net_correct'] = None
boxscores.loc[boxscores.Wmy_rank <
           boxscores.Lmy_rank, 'my_correct'] = 1
boxscores.loc[boxscores.Wmy_rank >
              boxscores.Lmy_rank, 'my_correct'] = 0
boxscores.loc[boxscores.Wkp_rank <
           boxscores.Lkp_rank, 'kp_correct'] = 1
boxscores.loc[boxscores.Wkp_rank >
              boxscores.Lkp_rank, 'kp_correct'] = 0
boxscores.loc[boxscores.Wnet_rank <
              boxscores.Lnet_rank, 'net_correct'] = 1
boxscores.loc[boxscores.Wnet_rank >
              boxscores.Lnet_rank, 'net_correct'] = 0

rankCorrectList = list(boxscores)[-3:]
#could then have elo rating correlated with the different ranking systems
#and then show each correlated with win_pct i.e. reflective of past performance



query = 'SELECT * FROM team'
team = read_sql_query(db, query)
team = team[['TeamID', 'TeamName']]
team = team.drop_duplicates(subset=['TeamID'])


seasons = list(rank['Season'].unique())
seasons.sort()
currentSeason = max(seasons)
seasons.append("All")
seasons_drop = map(str, seasons)  # convert values to string for dropdown
query = 'SELECT * FROM inSeasonAverages'
avg_stats = read_sql_query(db, query)
avg_stats = avg_stats.merge(team, how='inner', left_on=['TeamID'], right_on=['TeamID'])
avg_stats = avg_stats.sort_values(
    by='Date').reset_index(drop=True)
avg_stats.drop_duplicates(
    subset=['TeamID', 'roundDayNum', 'Season'], keep='last', inplace=True)
avg_stats = avg_stats[['Season', 'TeamID','TeamName', 'win_pct', 'roundDayNum']]

df = rank.merge(avg_stats, how='inner', left_on=[
    'Season', 'TeamID', 'roundDayNum'], right_on=['Season', 'TeamID', 'roundDayNum'])

df = df[['Season', 'Date', 'TeamName', 'TeamID', 'win_pct', 'my_rank','kp_rank','net_rank']]
df['Date'] = pd.to_datetime(df['Date'])
current_year = df.Date.dt.year.max()
df['Date'] = df['Date'].dt.date
rankList = list(df)[-3:]
nameList = list(df.TeamName.unique())
############
#filter df to min date, sort by rank, get :25
line_filter_df = df[(df['Season'] == currentSeason)]
#add option to switch rank system
first_date = line_filter_df['Date'].min() + timedelta(days=21)#starts 3 weeks after 1st rank
team_line_filter_df = line_filter_df[(line_filter_df['Date'] == first_date)]
team_line_filter_df = team_line_filter_df.sort_values(
    by='my_rank').reset_index(drop=True)
teamsListStart = team_line_filter_df.TeamName.tolist()[:25]
hiddenCols = ['Date', 'Season', 'TeamID','win_pct']
# removes hidden cols from df
columns = [x for x in list(df) if x not in hiddenCols]


######################## RANK Layout ########################
layout_rank_accuracy = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["My Rating"], style={'marginTop': 15})
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
        dbc.Row(
            dbc.Col(
                html.Div([
                    dcc.Dropdown(
                        id='rank-accuracy-team-dropdown',
                        options=[{"label": i, "value": i}
                                 for i in nameList],
                        value=teamsListStart,
                        multi=True
                    ),
                ])
            ),
            #id='graph-row'
        ),
        dcc.Loading(
            id='rank-accuracy-graphs-loading',
            type="default",
            children=dbc.Row(
                dbc.Col(
                    dcc.Graph(id="rank-rank-line-plot"),
                ),
                #id='graph-row'
            ),
        ),
        
        dcc.Loading(
            id='rank-accuracy-graphs-loading',
            type="default",
            children=dbc.Row([
                dbc.Col([
                    dcc.Graph(id="rank-rank-scatter-plot"),
                    dcc.Graph(id="kp-rank-scatter-plot"),
                    dcc.Graph(id="net-rank-scatter-plot"),
                ]),
                dbc.Col([
                    dcc.Graph(id="rank-rank-pie-plot"),
                    dcc.Graph(id="kp-rank-pie-plot"),
                    dcc.Graph(id="net-rank-pie-plot"),
                ]),
            ],
                #id='graph-row'
            )
        ),
        
    ], className="subpage")
], className="page")

######################## Callbacks ########################
#Callback for table
#########################################################

#scatter plots of each rank and it's correlation to win%
@app.callback([
    Output("rank-rank-scatter-plot", "figure"),
    Output("kp-rank-scatter-plot", "figure"),
    Output("net-rank-scatter-plot", "figure")],
    [Input('season-dropdown', 'value')])
def make_scatter_plot(season):
    graphs = []
    scatter_filter_df = df.copy()
    scatter_filter_df.dropna(subset=['my_rank', 'kp_rank',
                                     'net_rank'], inplace=True)
    if season == 'All':
        dfList = []
        for season in seasons:
            if season == 'All':
                continue
            season = int(season)#by default season i string
            scatter_filter_df = scatter_filter_df[(
                scatter_filter_df['Season'] == season)]
            # sort to get most recent for each ID
            scatter_filter_df = scatter_filter_df.sort_values(
                by='Date').reset_index(drop=True)
            scatter_filter_df.drop_duplicates(
                subset=['TeamID'], keep='last', inplace=True)
            dfList.append(scatter_filter_df)
        scatter_filter_df = pd.concat(dfList)
        for rank in rankList:
            graphs.append(px.scatter(scatter_filter_df, x=rank, y='win_pct', height=300))
    else:
        season = int(season)
        scatter_filter_df = scatter_filter_df[(
            scatter_filter_df['Season'] == season)]
        scatter_filter_df = scatter_filter_df.sort_values(
            by='Date').reset_index(drop=True)
        scatter_filter_df.drop_duplicates(
            subset=['TeamID'], keep='last', inplace=True)
        for rank in rankList:
            graphs.append(px.scatter(scatter_filter_df, x=rank, y = 'win_pct', height=300))
        return graphs[0], graphs[1], graphs[2]

#pie chart of each ranks accuracy in predicting a win/loss


@app.callback([
    Output("rank-rank-pie-plot", "figure"),
    Output("kp-rank-pie-plot", "figure"),
    Output("net-rank-pie-plot", "figure")],
    [Input('season-dropdown', 'value')])
def make_pie_plot(season):
    if season == 'All':
        graphs = []
        for rank in rankCorrectList:
            g = boxscores.groupby(rank)
            size = g.size()
            graphs.append(px.pie(boxscores, values=size, names=size, height=300))
        return graphs[0], graphs[1], graphs[2]
    else:
        season = int(season)
        filter_boxscores = boxscores[(boxscores['Season'] == season)]
        graphs = []
        for rank in rankCorrectList:
            g = filter_boxscores.groupby(rank)
            size = g.size()
            graphs.append(
                px.pie(boxscores, values=size, names=size.index, height=300, title=rank+' % Correct'))
        return graphs[0], graphs[1], graphs[2]
    

@app.callback(
    Output("rank-rank-line-plot", "figure"),
    [Input('rank-accuracy-team-dropdown', 'value'), Input('season-dropdown', 'value')])
def make_line_plot(teamsList, season):
    if season == 'All':
        season = 2020
    season = int(season)
    line_filter_df = df[(df['Season'] == season)]
    #ADD OPTION TO SWITCH RANK SYSTEM
    first_date = line_filter_df['Date'].min() + timedelta(days=21)#starts 3 weeks after 1st rank
    team_line_filter_df = line_filter_df[(line_filter_df['Date'] == first_date)]
    team_line_filter_df = team_line_filter_df.sort_values(
        by='my_rank').reset_index(drop=True)
    teamsList = team_line_filter_df.TeamName.tolist()[:25]
    #MAKE RESET FILTER FOR TEAMSLIST
    line_filter_df = line_filter_df[line_filter_df['TeamName'].isin(teamsList)]
    line_filter_df = line_filter_df[(line_filter_df['Date'] >= first_date)]
    return px.line(line_filter_df, x="Date", y="my_rank", color='TeamName', title='My Top 25 Rank over time')

############ UNUSED CALLBACKS ################################
#change in season changes date

#@app.callback(Output('rank-accuracy-date-picker-single', 'date'),
#              [Input('season-dropdown', 'value')])
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


#@app.callback([Output('datatable-rank-accuracy-rating', 'data'),
#               Output('rank-accuracy-date-picker-single', 'initial_visible_month')],
#              [Input('rank-accuracy-date-picker-single', 'date'),
#               Input('season-dropdown', 'value')])
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
            filter_df.drop_duplicates(
                subset=['TeamID'], keep='last', inplace=True)
            filter_df = filter_df.sort_values(
                by='my_rank').reset_index(drop=True)
            dfList.append(filter_df)
        filter_df = pd.concat(dfList)

    else:
        value = int(value)
        filter_df = df[(df['Season'] == value)]
        filter_df = filter_df[(filter_df['Date'] <= date)]
        # sort to get most recent for each ID
        filter_df.Date = pd.to_datetime(filter_df.Date)
        filter_df.drop_duplicates(
            subset=['TeamID'], keep='last', inplace=True)
        filter_df = filter_df.sort_values(by='my_rank').reset_index(drop=True)

    filter_dict = filter_df.to_dict("rows")
    #lol = filter_df.values.tolist()
    return filter_dict, new_month
