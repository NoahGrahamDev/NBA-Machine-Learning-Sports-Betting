import os
import random
import sqlite3
import sys
import time
from datetime import datetime, timedelta

import toml

sys.path.insert(1, os.path.join(sys.path[0], '../..'))
from src.Utils.tools import get_nfl_json_data, to_nfl_data_frame

config = toml.load("../../config.toml")

nfl_api_key = os.getenv('NFL_API_KEY')
if not nfl_api_key:
    print("Warning: NFL_API_KEY environment variable not set. API calls may fail.")

con = sqlite3.connect("../../Data/NFLTeamData.sqlite")

for season_key, season_config in config['get-nfl-data'].items():
    start_week = season_config['start_week']
    end_week = season_config['end_week']
    
    for week in range(start_week, end_week + 1):
        print(f"Getting NFL data: {season_key} Week {week}")
        
        team_stats_url = config['nfl_scores_url'].format(
            season=season_key, 
            week=week
        )
        
        raw_data = get_nfl_json_data(team_stats_url, nfl_api_key)
        df = to_nfl_data_frame(raw_data)
        
        if not df.empty:
            df['Season'] = season_key
            df['Week'] = week
            df.to_sql(f"{season_key}_week_{week}", con, if_exists="replace")
        
        time.sleep(random.randint(2, 5))

con.close()
