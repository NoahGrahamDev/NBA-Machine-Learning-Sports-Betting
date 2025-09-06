import re
from datetime import datetime

import pandas as pd
import requests

from src.Utils.Dictionaries import nfl_team_index_current

nfl_api_headers = {
    'Accept': 'application/json',
    'User-Agent': 'NFL-ML-Betting-System/1.0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

games_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/57.0.2987.133 Safari/537.36',
    'Dnt': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en',
    'Referer': 'https://github.com'
}


def get_nfl_json_data_thesportsdb(season, week=None):
    """
    Fetch NFL data from TheSportsDB API
    Args:
        season: NFL season year (e.g., 2019, 2020, etc.)
        week: Optional week number (not used in TheSportsDB, gets full season)
    Returns:
        List of game events for the season
    """
    base_url = "https://www.thesportsdb.com/api/v1/json/123"
    url = f"{base_url}/eventsseason.php?id=4391&s={season}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        events = data.get('events', [])
        if not events:
            print(f"No events found for season {season}")
            return []
            
        print(f"Retrieved {len(events)} games for {season} season")
        return events
        
    except Exception as e:
        print(f"Error fetching NFL data from TheSportsDB: {e}")
        return []

def get_nfl_json_data(url, api_key=None):
    """
    Legacy function for backward compatibility
    This function is deprecated - use get_nfl_json_data_thesportsdb instead
    """
    print("Warning: get_nfl_json_data is deprecated. Use get_nfl_json_data_thesportsdb instead.")
    headers = nfl_api_headers.copy()
    if api_key:
        headers['Ocp-Apim-Subscription-Key'] = api_key
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching NFL data: {e}")
        return {}

def get_json_data(url):
    raw_data = requests.get(url, headers=nfl_api_headers)
    try:
        json = raw_data.json()
    except Exception as e:
        print(e)
        return {}
    return json


def get_todays_games_json(url):
    raw_data = requests.get(url, headers=games_header)
    json = raw_data.json()
    return json.get('gs').get('g')


def to_nfl_data_frame_thesportsdb(json_data):
    """
    Convert TheSportsDB JSON data to DataFrame
    Maps TheSportsDB fields to standardized column names
    """
    if not json_data:
        return pd.DataFrame()
    
    mapped_data = []
    for game in json_data:
        mapped_game = {
            'GameKey': game.get('idEvent', ''),
            'Season': int(game.get('strSeason', 0)) if game.get('strSeason') else 0,
            'Date': game.get('dateEvent', ''),
            'HomeTeam': game.get('strHomeTeam', ''),
            'AwayTeam': game.get('strAwayTeam', ''),
            'HomeScore': int(game.get('intHomeScore', 0)) if game.get('intHomeScore') else 0,
            'AwayScore': int(game.get('intAwayScore', 0)) if game.get('intAwayScore') else 0,
            'HomeTeamID': game.get('idHomeTeam', ''),
            'AwayTeamID': game.get('idAwayTeam', ''),
            'EventName': game.get('strEvent', ''),
            'League': game.get('strLeague', 'NFL')
        }
        mapped_data.append(mapped_game)
    
    df = pd.DataFrame(mapped_data)
    return df

def to_nfl_data_frame(data):
    """
    Legacy function for backward compatibility
    This function is deprecated - use to_nfl_data_frame_thesportsdb instead
    """
    print("Warning: to_nfl_data_frame is deprecated. Use to_nfl_data_frame_thesportsdb instead.")
    if not data:
        return pd.DataFrame()
    
    if isinstance(data, list):
        return pd.DataFrame(data)
    else:
        return pd.DataFrame([data])

def to_data_frame(data):
    if not data:
        return pd.DataFrame(data={})
    
    if isinstance(data, list):
        return pd.DataFrame(data)
    else:
        return pd.DataFrame([data])


def create_todays_games(input_list):
    games = []
    for game in input_list:
        home = game.get('h')
        away = game.get('v')
        home_team = home.get('tc') + ' ' + home.get('tn')
        away_team = away.get('tc') + ' ' + away.get('tn')
        games.append([home_team, away_team])
    return games


def create_todays_games_from_odds(input_dict):
    games = []
    for game in input_dict.keys():
        home_team, away_team = game.split(":")
        if home_team not in nfl_team_index_current or away_team not in nfl_team_index_current:
            continue
        games.append([home_team, away_team])
    return games


def get_nfl_current_week():
    from datetime import datetime
    now = datetime.now()
    
    if now.month >= 9:
        season_start = datetime(now.year, 9, 1)
    else:
        season_start = datetime(now.year - 1, 9, 1)
    
    days_since_start = (now - season_start).days
    week = min(max(1, (days_since_start // 7) + 1), 18)
    return week

def handle_bye_weeks(team_name, week, season):
    bye_weeks = {
        2024: {
            'Arizona Cardinals': 11,
            'Atlanta Falcons': 12,
            'Baltimore Ravens': 14,
            'Buffalo Bills': 12,
            'Carolina Panthers': 11,
            'Chicago Bears': 7,
            'Cincinnati Bengals': 12,
            'Cleveland Browns': 10,
            'Dallas Cowboys': 7,
            'Denver Broncos': 14,
            'Detroit Lions': 5,
            'Green Bay Packers': 10,
            'Houston Texans': 14,
            'Indianapolis Colts': 14,
            'Jacksonville Jaguars': 12,
            'Kansas City Chiefs': 6,
            'Las Vegas Raiders': 10,
            'Los Angeles Chargers': 5,
            'Los Angeles Rams': 6,
            'Miami Dolphins': 6,
            'Minnesota Vikings': 6,
            'New England Patriots': 14,
            'New Orleans Saints': 12,
            'New York Giants': 11,
            'New York Jets': 12,
            'Philadelphia Eagles': 5,
            'Pittsburgh Steelers': 9,
            'San Francisco 49ers': 9,
            'Seattle Seahawks': 10,
            'Tampa Bay Buccaneers': 11,
            'Tennessee Titans': 5,
            'Washington Commanders': 14
        }
    }
    
    return bye_weeks.get(season, {}).get(team_name) == week

def get_date(date_string):
    match = re.search(r'(\d+)-\d+-(\d\d)(\d\d)', date_string)
    if not match:
        return None
    year1, month, day = match.groups()
    year = year1 if int(month) > 8 else int(year1) + 1
    return datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
