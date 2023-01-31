from pbpstats.client import Client
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation 
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network
import time
from nba_api.stats.endpoints import commonteamroster

settings = {
    "dir": "response_data",
    "Games": {"source": "file", "data_provider": "data_nba"},
    "Possessions": {"source": "file", "data_provider": "data_nba"},
    "EnhancedPbp": {"source": "file", "data_provider": "data_nba"}
}

client = Client(settings)
#s = client.Season("wnba", "2022", "Regular Season")

# Read dictionary keyed by team names and valued by team IDs
with open('../Team Info/WNBA_teams_dict.txt','r') as f:
    team_names_dict = eval(f.read())

team_ids_dict = {v:k for k,v in team_names_dict.items()}

game_data  = {'game_id': '1022200215',
 'date': '2022-08-14',
 'status': 'Final',
 'home_team_id': 1611661319,
 'home_team_abbreviation': 'LVA',
 'home_score': '109',
 'away_team_id': 1611661328,
 'away_team_abbreviation': 'SEA',
 'away_score': '100'}
game = client.Game(game_data['game_id'])
rosters = {}
networks = {}
frames = len(game.enhanced_pbp.items)

for team in ['home', 'away']:
    r = commonteamroster.CommonTeamRoster(season="2022", team_id=game_data[team+'_team_id'],league_id_nullable='10').get_data_frames()[0]
    rosters[game_data[team+'_team_id']] = dict(zip(r['PLAYER_ID'].tolist(),r['PLAYER'].tolist()))

    # Initialize team networks
    networks[game_data[team+'_team_id']] = nx.complete_graph(game.enhanced_pbp.items[0].current_players[game_data[team+'_team_id']])
    nx.set_edge_attributes(networks[game_data[team+'_team_id']],0,'weight')   

SEA = 1611661328
LVA = 1611661319

fig, ax = plt.subplots(1,2,figsize=(12,6))



plt.sca(ax[0])
nx.draw(networks[LVA])
plt.sca(ax[1])
nx.draw(networks[SEA])

def animate(frame):
    
    shot = game.enhanced_pbp.fgms[frame]
    
    shooting_team = shot.data['team_id']
    if shooting_team==LVA:
        plt.sca(ax[0])
    else:
        plt.sca(ax[1])
    plt.cla()
    shooting_team_network = networks[shooting_team]
    shooting_team_network.add_edges_from(nx.complete_graph(shot.current_players[shooting_team]).edges())
    if shot.data["player1_id"] in shooting_team_network.nodes:
        shooter = shot.data["player1_id"]
        for player in shot.current_players[shooting_team]:
            if player != shooter and player in shot.current_players[shooting_team]:
                try:
                    networks[shooting_team][player][shooter]['weight'] += shot.shot_data["ShotValue"]
                except:
                    networks[shooting_team][player][shooter]['weight'] = shot.shot_data["ShotValue"]
    
    name_labels = {k:v for k,v in rosters[shooting_team].items() if k in shooting_team_network.nodes()}
    nx.draw(shooting_team_network,pos=nx.circular_layout(shooting_team_network), \
            width=list(nx.get_edge_attributes(shooting_team_network,'weight').values()), edge_cmap=plt.cm.binary, \
            with_labels=True, labels=name_labels, font_color='g')

ani = FuncAnimation(fig, animate, frames=frames, interval=1000, repeat=True)

plt.show()

