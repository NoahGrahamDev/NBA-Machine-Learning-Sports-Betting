import requests
from datetime import datetime

def get_nfl_json_data(url):
    """Get NFL team stats data from API"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching NFL data: {e}")
        return []

def to_nfl_data_frame(data):
    """Convert NFL API data to DataFrame format"""
    import pandas as pd
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    return df

def load_nfl_team_stats_from_sqlite():
    """Load current NFL team stats from SQLite database for predictions"""
    import sqlite3
    import pandas as pd
    import numpy as np
    
    try:
        con = sqlite3.connect('Data/NFLDataset.sqlite')
        
        tables_to_try = ["nfl_dataset_2019-2025", "nfl_dataset_2019-24"]
        data = pd.DataFrame()
        table_used = None
        
        for table_name in tables_to_try:
            try:
                query = f'''
                SELECT * FROM "{table_name}" 
                WHERE Season = "2024" 
                ORDER BY Week DESC, TEAM_NAME
                '''
                data = pd.read_sql_query(query, con)
                if not data.empty:
                    table_used = table_name
                    break
            except Exception:
                continue
        
        if data.empty:
            print("Warning: No 2024 NFL data found in database")
            con.close()
            return pd.DataFrame()
        
        latest_week = data['Week'].max()
        print(f"Using data from week {latest_week} (most recent available)")
        
        recent_data = data[data['Week'] == latest_week]
        
        team_stats = []
        
        for _, row in recent_data.iterrows():
            home_team_data = {}
            for col in row.index:
                if not col.endswith('.1') and col not in ['Season', 'Week', 'Date', 'Score', 'Home-Team-Win', 'OU', 'OU-Cover', 'Days-Rest-Home', 'Days-Rest-Away']:
                    home_team_data[col] = row[col]
            if home_team_data.get('TEAM_NAME'):
                games_played = home_team_data.get('W', 0) + home_team_data.get('L', 0)
                if games_played > 0:
                    for stat in ['PTS', 'PTS_ALLOWED', 'PASS_YDS', 'RUSH_YDS', 'SACKS', 'TURNOVERS']:
                        if stat in home_team_data and pd.notna(home_team_data[stat]):
                            home_team_data[stat] = home_team_data[stat] / games_played
                    
                    home_team_data['W_PCT'] = home_team_data.get('W', 0) / games_played
                    home_team_data['GAMES_PLAYED'] = games_played
                
                home_team_data['Season'] = row['Season']
                home_team_data['Week'] = row['Week']
                home_team_data['Date'] = row['Date']
                team_stats.append(home_team_data)
            
            away_team_data = {}
            for col in row.index:
                if col.endswith('.1'):
                    base_col = col[:-2]
                    away_team_data[base_col] = row[col]
            if away_team_data.get('TEAM_NAME'):
                games_played = away_team_data.get('W', 0) + away_team_data.get('L', 0)
                if games_played > 0:
                    for stat in ['PTS', 'PTS_ALLOWED', 'PASS_YDS', 'RUSH_YDS', 'SACKS', 'TURNOVERS']:
                        if stat in away_team_data and pd.notna(away_team_data[stat]):
                            away_team_data[stat] = away_team_data[stat] / games_played
                    
                    away_team_data['W_PCT'] = away_team_data.get('W', 0) / games_played
                    away_team_data['GAMES_PLAYED'] = games_played
                
                away_team_data['Season'] = row['Season']
                away_team_data['Week'] = row['Week']
                away_team_data['Date'] = row['Date']
                team_stats.append(away_team_data)
        
        team_df = pd.DataFrame(team_stats)
        if team_df.empty:
            con.close()
            return pd.DataFrame()
        
        team_df = team_df.drop_duplicates(subset=['TEAM_NAME'], keep='first')
        
        numeric_columns = team_df.select_dtypes(include=[np.number]).columns
        team_df = team_df.copy()  # Avoid SettingWithCopyWarning
        team_df[numeric_columns] = team_df[numeric_columns].fillna(0)
        
        con.close()
        print(f"Loaded {len(team_df)} teams from {table_used} using most recent available data")
        print(f"Final dataset: {len(team_df)} teams total")
        return team_df
        
    except Exception as e:
        print(f"Error loading NFL data from SQLite: {e}")
        return pd.DataFrame()

def get_nfl_current_week():
    """Get current NFL week number"""
    current_date = datetime.now()
    
    if current_date.month >= 9 or current_date.month <= 2:
        week_start = datetime(current_date.year if current_date.month >= 9 else current_date.year - 1, 9, 1)
        days_since_start = (current_date - week_start).days
        week = min(max(1, (days_since_start // 7) + 1), 18)
        return week
    else:
        return 1
