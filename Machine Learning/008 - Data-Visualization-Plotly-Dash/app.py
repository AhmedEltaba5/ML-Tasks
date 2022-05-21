# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 01:08:38 2021

@author: ahmed eltabakh
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.graph_objects as go

# Load data
df = pd.read_csv('data/processed_df.csv', index_col=0, parse_dates=True)

# drop duplicates
df = df.drop_duplicates(subset=['full', 'round'])

top_goals_player = df.groupby('full').sum().reset_index()[['full', 'goals_scored']].sort_values(by='goals_scored',\
                                                                                                 ascending=False)[0:10]
top_assists_player = df.groupby('full').sum().reset_index()[['full', 'assists']].sort_values(by='assists',\
                                                                                                 ascending=False)[0:10]
## Grouped DF
grouped_player_df = df.groupby('full').sum().reset_index()

import dash
from dash import html
from dash import dcc #data control components
from dash.dependencies import Input, Output

app = dash.Dash(external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', 'assets/own_style.css'])

#Start Figure
def plot_bar_player(player_name):
    total_points_player = df[df['full'] == player_name].groupby('round').sum().reset_index()[['round', 'total_points']]
    max_points_df = df.groupby('round').max()['total_points'].reset_index()
    merged_df = total_points_player.merge(max_points_df, on='round', how='left')
    fig_bar = go.Figure()
    # Add traces
    fig_bar.add_trace(
        go.Bar(x=merged_df["round"], y=merged_df["total_points_x"], width=0.4, name='Player Points',\
               marker_color='rgb(26, 118, 255)')
        
    )
    
    fig_bar.add_trace(
        go.Bar(x=merged_df["round"], y=merged_df["total_points_y"], opacity=0.2, name='Max Points',\
        marker_color='rgb(26, 118, 255)')
    )
    
    fig_bar.update_layout(
        title=dict(text='Player Points Across All Rounds', y=0.9,x=0.5, xanchor= 'center',yanchor= 'top'),
        xaxis_tickfont_size=10,
        xaxis = dict(
            title= 'Rounds',
            tickmode = 'linear',
            tick0 = 1,
            dtick = 1
        ),
        yaxis=dict(
            title='Total Points',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    
    return fig_bar

# end figure

def get_goals_player(player_name):
    ## Total Goals by player
    total_goals = grouped_player_df[grouped_player_df['full'] == player_name]['goals_scored']
    
    return total_goals

def get_assists_player(player_name):
    ## Total Assists by player
    total_assists = grouped_player_df[grouped_player_df['full'] == player_name]['assists']
    
    return total_assists

def get_points_player(player_name):
    ## Total Points by player
    total_points = grouped_player_df[grouped_player_df['full'] == player_name]['total_points']
    
    return total_points

# Top Players Goals
fig_goals = px.bar(top_goals_player, x="full", y="goals_scored", text='goals_scored',\
            labels={'full':'Player Name', 'goals_scored': 'Goals Scored'}) 
fig_goals.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig_goals.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickangle=-90,\
                  title={'text': 'Top 10 Players To Score','y':0.96,'x':0.5, 'xanchor': 'center','yanchor': 'top'})

fig_goals.show()
# end Top Players Goals

# Top Assists 
fig_assists = px.bar(top_assists_player, x="full", y="assists", text='assists',\
            labels={'full':'Player Name', 'assists': 'Assists'}) 
fig_assists.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig_assists.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickangle=-90,\
                  title={'text': 'Top 10 Players To Assist','y':0.96,'x':0.5, 'xanchor': 'center','yanchor': 'top'})
fig_assists.show()
# End Assists

app.layout = html.Div([
    html.H1('Fantasy Premier League Dashboard'),
    html.Div([
             html.Div([
                    html.Pre(children="Select Player:", style={"fontSize": "150%"}),
                    dcc.Dropdown(
                    id='myDropdown',
                    options = [
                        {'label': str(player), 'value': str(player)} for player in df['full'].unique()
                        ], value='Mohamed Salah',
                    placeholder='choose a player...'
                    )
                 ], className='three columns'),
             html.Div([
                       html.Div([
                                html.Div([
                                         html.Div([html.Img(src='salah.png', id='img')], className='ban-text name'),
                                         ], className='two columns'),
                                html.Div([html.Div([html.P(id='p_player')], className='ban-text name')], className='four columns'),
                                html.Div([
                                           html.Div([], id='goal', className='ban-text num'),
                                           html.Span(['Goal'],className='ban-span'),
                                           html.Div([], id='assist', className='ban-text num'),
                                           html.Span(['Assist'],className='ban-span'),
                                           html.Div([], id='point', className='ban-text num'),
                                           html.Span(['Point'],className='ban-span')
                                         ], className='eight columns')
                                ], className='row')
                
                       ], id='ban', className='nine columns', style={'margin':'0'}),
             ], className='row'),
    html.Div([
            html.Div([dcc.Graph(id='player')], className='twelve columns'),
        ], className='row'),
    
    html.Div([html.Div([html.H1('Top 10 Players')], className='title')], className='row'),

    html.Div([
            html.Div([dcc.Graph(figure=fig_goals)], className='six columns'),
            html.Div([dcc.Graph(figure=fig_assists)], className='six columns')
        ], className='row')
    
    ])

@app.callback(
    Output('player', 'figure'),
    Output(component_id='p_player',component_property='children'),
    Output(component_id='goal',component_property='children'),
    Output(component_id='assist',component_property='children'),
    Output(component_id='point',component_property='children'),
    Output(component_id='img',component_property='src'),
    Input('myDropdown', 'value')
)
def update_output(value):
    if (value == 'Mohamed Salah'):
        #image
        player_img = 'https://resources.premierleague.com/premierleague/photos/players/250x250/p118748.png'
    elif (value == 'Riyad Mahrez'):
        #image
        player_img = 'https://resources.premierleague.com/premierleague/photos/players/250x250/p103025.png'
    elif (value == 'Jamie Vardy'):
        #image
        player_img = 'http://i2.wp.com/infonetworth.com/wp-content/uploads/2021/08/Jamie-Vardy-Net-Worth.jpg'
    else:
        player_img = 'https://thumbs.dreamstime.com/b/male-soccer-player-avatar-man-playing-sport-character-profile-user-person-people-icon-vector-illustration-isolated-220472407.jpg'
    return plot_bar_player(value), value, get_goals_player(value), get_assists_player(value), get_points_player(value), player_img

"""
# function to select the player
@app.callback(
    Output('graph2', 'figure'),
    State('myDropdown', 'value'))

def update_figure(player_name):
    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55)

    fig.update_layout(transition_duration=500)

    return fig
"""

app.run_server()



