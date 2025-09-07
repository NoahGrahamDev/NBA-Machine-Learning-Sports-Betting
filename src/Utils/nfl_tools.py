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
    
    try:
        con = sqlite3.connect('Data/NFLDataset.sqlite')
        query = '''
        SELECT * FROM "nfl_dataset_2019-24" 
        WHERE Season = "2024" 
        ORDER BY Week DESC
        '''
        data = pd.read_sql_query(query, con)
        con.close()
        
        if data.empty:
            print("Warning: No 2024 NFL data found in database")
            return pd.DataFrame()
        
        latest_week = data['Week'].max()
        current_data = data[data['Week'] == latest_week]
        
        team_stats = []
        
        for _, row in current_data.iterrows():
            home_team_data = {}
            for col in row.index:
                if not col.endswith('.1') and col not in ['Season', 'Week', 'Date', 'Score', 'Home-Team-Win', 'OU', 'OU-Cover', 'Days-Rest-Home', 'Days-Rest-Away']:
                    home_team_data[col] = row[col]
            team_stats.append(home_team_data)
            
            away_team_data = {}
            for col in row.index:
                if col.endswith('.1'):
                    base_col = col[:-2]  # Remove .1 suffix
                    away_team_data[base_col] = row[col]
                elif col in ['Season', 'Week', 'Date']:
                    away_team_data[col] = row[col]
            team_stats.append(away_team_data)
        
        team_df = pd.DataFrame(team_stats)
        
        team_df = team_df.drop_duplicates(subset=['TEAM_NAME'], keep='first')
        
        print(f"Loaded {len(team_df)} teams from SQLite database for week {latest_week}")
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
