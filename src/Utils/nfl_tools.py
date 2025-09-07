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
        
        tables_to_try = ["nfl_dataset_2019-2025", "nfl_dataset_2019-24"]
        data = pd.DataFrame()
        table_used = None
        
        for table_name in tables_to_try:
            try:
                query = f'''
                SELECT * FROM "{table_name}" 
                WHERE Season = "2024" 
                ORDER BY Week DESC
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
        
        available_weeks = sorted(data['Week'].unique(), reverse=True)
        team_df = pd.DataFrame()
        
        for week in available_weeks:
            week_data = data[data['Week'] == week]
            team_stats = []
            
            for _, row in week_data.iterrows():
                home_team_data = {}
                for col in row.index:
                    if not col.endswith('.1') and col not in ['Season', 'Week', 'Date', 'Score', 'Home-Team-Win', 'OU', 'OU-Cover', 'Days-Rest-Home', 'Days-Rest-Away']:
                        home_team_data[col] = row[col]
                if home_team_data.get('TEAM_NAME'):
                    team_stats.append(home_team_data)
            
            for _, row in week_data.iterrows():
                away_team_data = {}
                for col in row.index:
                    if col.endswith('.1'):
                        base_col = col[:-2]
                        away_team_data[base_col] = row[col]
                    elif col in ['Season', 'Week', 'Date']:
                        away_team_data[col] = row[col]
                if away_team_data.get('TEAM_NAME'):
                    team_stats.append(away_team_data)
            
            week_df = pd.DataFrame(team_stats)
            week_df = week_df.drop_duplicates(subset=['TEAM_NAME'], keep='first')
            
            if team_df.empty:
                team_df = week_df.copy()
                print(f"Loaded {len(team_df)} teams from {table_used} for week {week}")
            else:
                existing_teams = set(team_df['TEAM_NAME'])
                new_teams = set(week_df['TEAM_NAME']) - existing_teams
                if new_teams:
                    missing_data = week_df[week_df['TEAM_NAME'].isin(new_teams)]
                    team_df = pd.concat([team_df, missing_data], ignore_index=True)
                    print(f"Added {len(new_teams)} missing teams from week {week}: {sorted(new_teams)}")
            
            if len(team_df) >= 30:
                break
        
        con.close()
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
