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

def normalize_team_name(team_name):
    """Normalize team names to handle variations"""
    name_mapping = {
        'Washington': 'Washington Commanders',
        'Washington Redskins': 'Washington Commanders'
    }
    return name_mapping.get(team_name, team_name)

def _extract_team_stats(row, team_name, is_home=True):
    """Extract team statistics from a row"""
    if is_home:
        team_data = {}
        for col in row.index:
            if not col.endswith('.1') and col not in ['Season', 'Week', 'Date', 'Score', 'Home-Team-Win', 'OU', 'OU-Cover', 'Days-Rest-Home', 'Days-Rest-Away']:
                team_data[col] = row[col]
    else:
        team_data = {}
        for col in row.index:
            if col.endswith('.1'):
                base_col = col[:-2]
                team_data[base_col] = row[col]
    
    team_data['TEAM_NAME'] = team_name
    return team_data

def load_nfl_team_stats_from_sqlite():
    """Load current NFL team stats from SQLite database for predictions"""
    import sqlite3
    import pandas as pd
    import numpy as np
    
    try:
        con = sqlite3.connect('Data/NFLDataset.sqlite')
        
        table_names = ['nfl_dataset_2019-2025', 'nfl_dataset_2019-24', 'nfl_dataset_2019-2024']
        data = pd.DataFrame()
        table_used = None
        
        for table_name in table_names:
            try:
                query = f'''
                SELECT * FROM "{table_name}" 
                WHERE Season IN ("2024", "2023", "2022", "2021") 
                ORDER BY Season DESC, Week DESC, TEAM_NAME
                '''
                data = pd.read_sql_query(query, con)
                if not data.empty:
                    table_used = table_name
                    break
            except Exception:
                continue
        
        if data.empty:
            print("Warning: No NFL data found in database")
            con.close()
            return pd.DataFrame()
        
        print(f"Using multi-season data (2021-2024) for complete team coverage")
        
        data['TEAM_NAME'] = data['TEAM_NAME'].apply(normalize_team_name)
        data['TEAM_NAME.1'] = data['TEAM_NAME.1'].apply(normalize_team_name)
        
        home_teams = set(data['TEAM_NAME'].unique())
        away_teams = set(data['TEAM_NAME.1'].unique())
        all_teams = home_teams.union(away_teams)
        
        team_stats = []
        
        for team in all_teams:
            team_home_data = data[data['TEAM_NAME'] == team]
            team_away_data = data[data['TEAM_NAME.1'] == team]
            
            if not team_home_data.empty:
                latest_home = team_home_data.iloc[0]
                team_data = _extract_team_stats(latest_home, team, is_home=True)
                
                games_played = team_data.get('W', 0) + team_data.get('L', 0)
                if games_played > 0:
                    for stat in ['PTS', 'PTS_ALLOWED', 'PASS_YDS', 'RUSH_YDS', 'SACKS', 'TURNOVERS']:
                        if stat in team_data and pd.notna(team_data[stat]):
                            team_data[stat] = team_data[stat] / games_played
                    
                    team_data['W_PCT'] = team_data.get('W', 0) / games_played
                    team_data['GAMES_PLAYED'] = games_played
                
                team_data['Season'] = latest_home['Season']
                team_data['Week'] = latest_home['Week']
                team_data['Date'] = latest_home['Date']
                team_stats.append(team_data)
                
            elif not team_away_data.empty:
                latest_away = team_away_data.iloc[0]
                team_data = _extract_team_stats(latest_away, team, is_home=False)
                
                games_played = team_data.get('W', 0) + team_data.get('L', 0)
                if games_played > 0:
                    for stat in ['PTS', 'PTS_ALLOWED', 'PASS_YDS', 'RUSH_YDS', 'SACKS', 'TURNOVERS']:
                        if stat in team_data and pd.notna(team_data[stat]):
                            team_data[stat] = team_data[stat] / games_played
                    
                    team_data['W_PCT'] = team_data.get('W', 0) / games_played
                    team_data['GAMES_PLAYED'] = games_played
                
                team_data['Season'] = latest_away['Season']
                team_data['Week'] = latest_away['Week']
                team_data['Date'] = latest_away['Date']
                team_stats.append(team_data)
        
        team_df = pd.DataFrame(team_stats)
        if team_df.empty:
            con.close()
            return pd.DataFrame()
        
        team_df = team_df.drop_duplicates(subset=['TEAM_NAME'], keep='first')
        
        numeric_columns = team_df.select_dtypes(include=[np.number]).columns
        team_df = team_df.copy()
        team_df[numeric_columns] = team_df[numeric_columns].fillna(0)
        
        con.close()
        print(f"Loaded {len(team_df)} teams from {table_used} using multi-season aggregation")
        print(f"Final dataset: {len(team_df)} teams total")
        return team_df
        
    except Exception as e:
        print(f"Error loading NFL team stats: {e}")
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
