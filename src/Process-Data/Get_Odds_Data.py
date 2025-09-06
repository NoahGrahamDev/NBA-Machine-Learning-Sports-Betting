import os
import random
import sqlite3
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
import toml
from sbrscrape import Scoreboard

sys.path.insert(1, os.path.join(sys.path[0], '../..'))
from src.Utils.Dictionaries import nfl_team_index_current

sportsbook = 'fanduel'
sport = 'NFL'
df_data = []

config = toml.load("../../config.toml")

con = sqlite3.connect("../../Data/NFLOddsData.sqlite")

for season_key, season_config in config['get-nfl-odds-data'].items():
    start_week = season_config['start_week']
    end_week = season_config['end_week']
    teams_last_played = {}
    
    for week in range(start_week, end_week + 1):
        print(f"Getting NFL odds data: {season_key} Week {week}")
        
        week_start = datetime(int(season_key), 9, 1) + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        current_date = week_start.date()
        while current_date <= week_end.date():
            sb = Scoreboard(date=current_date, sport=sport)

            if not hasattr(sb, "games") or not sb.games:
                current_date = current_date + timedelta(days=1)
                continue

            for game in sb.games:
                home_team = game['home_team']
                away_team = game['away_team']
                
                if home_team not in nfl_team_index_current or away_team not in nfl_team_index_current:
                    continue
                
                if home_team not in teams_last_played:
                    teams_last_played[home_team] = current_date
                    home_games_rested = timedelta(days=7)
                else:
                    home_games_rested = current_date - teams_last_played[home_team]
                    teams_last_played[home_team] = current_date

                if away_team not in teams_last_played:
                    teams_last_played[away_team] = current_date
                    away_games_rested = timedelta(days=7)
                else:
                    away_games_rested = current_date - teams_last_played[away_team]
                    teams_last_played[away_team] = current_date

                try:
                    df_data.append({
                        'Date': current_date,
                        'Season': season_key,
                        'Week': week,
                        'Home': home_team,
                        'Away': away_team,
                        'OU': game['total'][sportsbook],
                        'Spread': game['away_spread'][sportsbook],
                        'ML_Home': game['home_ml'][sportsbook],
                        'ML_Away': game['away_ml'][sportsbook],
                        'Points': game['away_score'] + game['home_score'],
                        'Win_Margin': game['home_score'] - game['away_score'],
                        'Days_Rest_Home': home_games_rested.days,
                        'Days_Rest_Away': away_games_rested.days
                    })
                except KeyError:
                    print(f"No {sportsbook} odds data found for game: {game}")

            current_date = current_date + timedelta(days=1)
            time.sleep(random.randint(1, 3))

    df = pd.DataFrame(df_data)
    df.to_sql(season_key, con, if_exists="replace")
    df_data = []

con.close()
