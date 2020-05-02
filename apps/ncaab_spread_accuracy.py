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

#CURRENTLY USING ADJUSTED MY_PERF TABLE FOR FALSE 2020 Spread PERF

####################### Read in data ############################
#read in 2020 by default, refresh for anything else
#in production read in all data into memory, will just slow app startup (not for user) but make server side callbacks quicker
db = 'ncaab'  # connects to local db
query = 'SELECT * FROM my_perf'
perf = read_sql_query(db, query)
query = 'SELECT * FROM boxscores'
box = read_sql_query(db, query)
box = box[['Date','WTeamID','LTeamID','WLoc']]
perf = perf.merge(box, how='inner', left_on=[
    'Date', 'WTeamID', 'LTeamID'], right_on=['Date', 'WTeamID', 'LTeamID'])
#perf = perf[(perf['Season'] == 2020)]
print(perf.shape)
perf.drop_duplicates(
    subset=['WTeamID','LTeamID','Date'], keep=False, inplace=True)
#test filtering rules for performance
# get only performance with normalized line

#no filter = -18k,2945
#-16 = -12.55k, 2428
#-14 = -10.19k, 2281
#-12 = -10.54k, 2121
#-10 = -9.18k, 1933
#-8 = 7.14k, 1624
#-6 = -3.22k, 1234 #optimal range to select
#-4 = -2.15k, 876
#No Neutral = -18.76k, 2649#no neutral doesn't help
#perf['line_diff'] = abs(perf['my_Spread_Line']-perf['house_Spread_Line'])
perf = perf[(perf['Season'] >= 2015)]
perf = perf[(perf['Date'].dt.month != 11)]#
perf = perf[(perf['my_Spread_Line'] <= 12)]#-10.19
#perf = perf[(perf['WLoc'] != 'N')]
#diff
#1.5> -15.24, 1614
#2.5 -8.512, 916
#3.5 -5.5, 513# line diff doesn't help
#perf = perf[(perf['line_diff'] >= 3.5)]#
print(perf.shape)
#perf = perf[['Season','Date','WTeamID','LTeamID','spread_profit']]

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
layout_spread_accuracy = html.Div([
    html.Div([
        # CC Header
        Header(),
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H6(["Spread Prediction Performance"], style={'marginTop': 15})
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
            id='spread-accuracy-graphs-loading',
            type="default",
            children=dbc.Row(
                dbc.Col(
                    dcc.Graph(id="spread-perf-waterfall-plot"),
                ),
                #id='graph-row'
            ),
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Button(
                            "What happened in 2020?",
                            id="2020-explanation-collapse-button",
                            className="mb-3",
                            color="primary",
                        ),
                        dbc.Collapse(
                            dbc.Card(dbc.CardBody(
                                "2020 is the first year that was used as an actual live test. This means that in the previous years our model fit the pattern for games, but couldn't generalize quite as well with future predictions. Nevertheless, there was a positive return.")),
                            id="2020-explanation-collapse",
                        ),
                    ]
                )
            )
        ),
        html.Div([
            html.Pre(id='relayout-data'),
        ], className='three columns'),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id="spread-accuracy-pie-plot")
            #dcc.Loading(
            #    id='spread-accuracy-pie-loading',
            #    type="default",
            #   children=
                    #id='graph-row'
            #    )
            ),
            dbc.Col(
                html.Div(
                [html.H6(id="spread-winnings-per-100-text"), html.P("Winnings per $100 bet")],
                id="wells",
                className="mini_container",
            ),
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="total-spread-winnings-text"), html.P("Total winnings given $100 bet a game")],
                    id="gas",
                    className="mini_container",
                ),
            ),
            dbc.Col(
                html.Div(
                    [html.H6(id="spread-pct-above-house-edge"),
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
@app.callback(
    Output("2020-explanation-collapse", "is_open"),
    [Input("2020-explanation-collapse-button", "n_clicks")],
    [State("2020-explanation-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(Output('spread-perf-waterfall-plot', 'figure'), [Input('season-dropdown', 'value')])

def spreadWaterfall(season):
    if season == 'All':
        perf_filter_df = perf.sort_values(
            by='Date').reset_index(drop=True)
        dates = list(perf_filter_df['Date'].unique())
        spread_profit = perf_filter_df.groupby(['Date'])['spread_profit'].sum()
        graph = go.Figure(go.Waterfall(
            name="20", orientation="v",
            #measure=["relative", "relative", "total",
            #         "relative", "relative", "total"],#may find a way to total each year
            x=dates,
            #textposition="outside",
            #text=["+60", "+80", "", "-40", "-20", "Total"],
            y=spread_profit,
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
        spread_profit = perf_filter_df.groupby(['Date'])['spread_profit'].sum()
        graph = go.Figure(go.Waterfall(
            name="20", orientation="v",
            x=dates,
            y=spread_profit
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
#    [Input('spread-perf-waterfall-plot', 'relayoutData')])
#def display_relayout_data(relayoutData):
#    return json.dumps(relayoutData, indent=2)
@app.callback([
    Output("spread-accuracy-pie-plot", "figure"),
    Output("spread-winnings-per-100-text", "children"),
    Output("total-spread-winnings-text", "children"),
    Output("spread-pct-above-house-edge", "children")],
    [Input('spread-perf-waterfall-plot', 'relayoutData'), Input('season-dropdown', 'value')])
def make_pie_plot(date_range,season):
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
    g = perf_filter_df.groupby('spread_correct')
    size = g.size()
    #convert to dollars and percent
    average_bet_profit = '${:,.2f}'.format(perf_filter_df.spread_profit.mean())
    total_bet_winnings = '${:,.2f}'.format(perf_filter_df.spread_profit.sum())
    #TEMP
    totalGames = len(perf_filter_df.index)
    above_house_edge = "{:.0%}".format(float(size.get(key='1'))/totalGames-float(size.get(key='0'))/totalGames)
    graph = px.pie(perf_filter_df, values=size, names=size.index, height=300, title='Spread % Correct')
    return graph, average_bet_profit, total_bet_winnings, above_house_edge



#def update_text(data):
#    return data[0] + " mcf", data[1] + " bbl", data[2] + " bbl"


#LOGIC TO ADD MULTIPLE LINE BREAKS WITH DATE RANGES OF SEASONS, MAY NOT WORK WITH WATERFALL OR AT ALL
        #for first season get max date, for next season get min date
        #subtract next season min date from max date to get number of days between
        #run loop to get each date into list
        #breakDateList = []
        #for season in seasonsList:
        #    try:
        #        season = int(season)
        #        print(season)
        #        prevSeasonEnd = perf_filter_df[(
        #            perf_filter_df['Season'] == season)]['Date'].max()
        #        print(prevSeasonEnd)
        #        nextSeasonBeg = perf_filter_df[(
        #            perf_filter_df['Season'] == season+1)]['Date'].min()
        #        print(nextSeasonBeg)
        #        numdays = (nextSeasonBeg - prevSeasonEnd).days
        #        print(numdays)#
        #        date_list = [prevSeasonEnd + timedelta(days=x) for x in range(numdays)]
        #        #print(date_list)
        #        breakDateList.extend(date_list)
        #        date_list=[]
        #    except Exception as e:
        #        print(e)
        #        break
        #
        #convert datetime.date to string
        #breakDateList = [date_obj.strftime('%Y-%m-%d') for date_obj in breakDateList]
        #print(breakDateList)
        #put breaks for dates between seasons
        #graph.update_xaxes(
        #    rangebreaks=[
        #        dict(values=breakDateList)
        #    ]
        #)
