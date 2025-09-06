# TheSportsDB Migration Guide

## Overview
This guide shows how to migrate from sportsdata.io to TheSportsDB for free NFL historical data access.

## Current vs New API Comparison

### Current sportsdata.io Structure
```python
# Current API call
url = "https://api.sportsdata.io/v3/nfl/scores/json/ScoresByWeek/2019/1"
headers = {'Ocp-Apim-Subscription-Key': api_key}
response = requests.get(url, headers=headers)
```

### New TheSportsDB Structure
```python
# New API call (no API key required)
url = "https://www.thesportsdb.com/api/v1/json/123/eventsseason.php?id=4391&s=2019"
response = requests.get(url)
```

## Key API Endpoints

### TheSportsDB NFL Endpoints
```python
base_url = "https://www.thesportsdb.com/api/v1/json/123"

# Get all games for a season
season_games = f"{base_url}/eventsseason.php?id=4391&s={year}"

# Get past games (recent)
past_games = f"{base_url}/eventspastleague.php?id=4391"

# Get upcoming games
upcoming_games = f"{base_url}/eventsnextleague.php?id=4391"

# Get league info
league_info = f"{base_url}/lookupleague.php?id=4391"

# Get team info
team_info = f"{base_url}/lookupteam.php?id={team_id}"
```

### NFL League and Team IDs
- **NFL League ID**: 4391
- **Team IDs**: Available in API responses (e.g., Atlanta Falcons = 134942)

## Data Structure Mapping

### sportsdata.io Response
```json
[
  {
    "GameKey": "202019001",
    "SeasonType": 1,
    "Season": 2019,
    "Week": 1,
    "Date": "2019-09-05T20:20:00",
    "AwayTeam": "GB",
    "HomeTeam": "CHI",
    "AwayScore": 10,
    "HomeScore": 3
  }
]
```

### TheSportsDB Response
```json
{
  "events": [
    {
      "idEvent": "600748",
      "strEvent": "Atlanta Falcons vs Denver Broncos",
      "strSeason": "2019",
      "dateEvent": "2019-08-01",
      "strHomeTeam": "Atlanta Falcons",
      "strAwayTeam": "Denver Broncos",
      "intHomeScore": "10",
      "intAwayScore": "14",
      "strLeague": "NFL",
      "idHomeTeam": "134942",
      "idAwayTeam": "134930"
    }
  ]
}
```

## Migration Steps

### Step 1: Update tools.py
Replace the `get_nfl_json_data` function:

```python
def get_nfl_json_data_thesportsdb(season, week=None):
    """
    Fetch NFL data from TheSportsDB
    """
    base_url = "https://www.thesportsdb.com/api/v1/json/123"
    
    if week:
        # For weekly data, get full season and filter
        url = f"{base_url}/eventsseason.php?id=4391&s={season}"
    else:
        # Get full season
        url = f"{base_url}/eventsseason.php?id=4391&s={season}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if week and 'events' in data:
            # Filter by week if needed (you'll need to implement week logic)
            return data['events']
        
        return data.get('events', [])
    except Exception as e:
        print(f"Error fetching NFL data from TheSportsDB: {e}")
        return []
```

### Step 2: Update config.toml
Replace sportsdata.io URLs with TheSportsDB endpoints:

```toml
[thesportsdb-nfl-data]
base_url = "https://www.thesportsdb.com/api/v1/json/123"
league_id = "4391"

[get-nfl-data]
    [get-nfl-data.2019]
        start_week = 1
        end_week = 17
        season_type = "REG"
    [get-nfl-data.2020]
        start_week = 1
        end_week = 17
        season_type = "REG"
    # ... continue for other seasons
```

### Step 3: Update Get_Data.py
Modify the main data fetching logic:

```python
# Remove API key requirement
# nfl_api_key = get_nfl_api_key()  # No longer needed

# Update data fetching loop
for season in config["get-nfl-data"]:
    season_data = get_nfl_json_data_thesportsdb(season)
    
    # Process the data (you'll need to adapt to new structure)
    for game in season_data:
        # Map TheSportsDB fields to your database schema
        processed_game = {
            'season': game['strSeason'],
            'date': game['dateEvent'],
            'home_team': game['strHomeTeam'],
            'away_team': game['strAwayTeam'],
            'home_score': int(game['intHomeScore']) if game['intHomeScore'] else 0,
            'away_score': int(game['intAwayScore']) if game['intAwayScore'] else 0,
        }
        # Insert into database
```

### Step 4: Remove API Key Dependencies
1. Remove `api_keys.txt` requirement
2. Remove API key validation
3. Update error handling for new API structure

## Testing the Migration

### Test Script
```python
import requests

def test_thesportsdb_access():
    """Test TheSportsDB API access for all required seasons"""
    base_url = "https://www.thesportsdb.com/api/v1/json/123"
    seasons = [2019, 2020, 2021, 2022, 2023, 2024]
    
    for season in seasons:
        url = f"{base_url}/eventsseason.php?id=4391&s={season}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('events', [])
            print(f"✅ Season {season}: {len(games)} games available")
        else:
            print(f"❌ Season {season}: Failed with status {response.status_code}")

if __name__ == "__main__":
    test_thesportsdb_access()
```

## Advantages of Migration

1. **No API Key Required**: Eliminates authentication issues
2. **No Subscription Limits**: Free access to all historical data
3. **Reliable Service**: 9+ years of operation
4. **Similar Data Structure**: Easier migration than other alternatives
5. **Rate Limits**: 30 requests/minute sufficient for batch processing

## Potential Challenges

1. **Data Structure Differences**: Field names and formats differ
2. **Week Organization**: May need to implement week filtering logic
3. **Team Name Mapping**: Full team names vs abbreviations
4. **Date Formats**: Different date/time formatting

## Rate Limiting Considerations

- **Free Tier**: 30 requests per minute
- **For 6 seasons**: ~6 requests total (one per season)
- **Well within limits**: No rate limiting concerns for your use case

This migration should resolve your sportsdata.io subscription limitations while providing the same historical data coverage you need for machine learning.
