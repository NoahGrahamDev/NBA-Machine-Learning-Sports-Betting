import os
import random
import sqlite3
import sys
import time
from datetime import datetime, timedelta

import toml

sys.path.insert(1, os.path.join(sys.path[0], '../..'))
from src.Utils.tools import get_nfl_json_data_thesportsdb, to_nfl_data_frame_thesportsdb

config = toml.load("../../config.toml")

con = sqlite3.connect("../../Data/NFLTeamData.sqlite")

for season_key, season_config in config['get-nfl-data'].items():
    print(f"Getting NFL data: {season_key} season")
    
    json_data = get_nfl_json_data_thesportsdb(season_key)
    
    if json_data:
        df = to_nfl_data_frame_thesportsdb(json_data)
        if not df.empty:
            df.to_sql("team_scores", con, if_exists="append", index=False)
            print(f"Saved {len(df)} games for {season_key} season")
        else:
            print(f"No data to save for {season_key} season")
    else:
        print(f"Failed to retrieve data for {season_key} season")
    
    time.sleep(2)

con.close()
