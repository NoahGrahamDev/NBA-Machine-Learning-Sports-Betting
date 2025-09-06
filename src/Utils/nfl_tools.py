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
