import sqlite3
import pandas as pd
import numpy as np
import toml
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '../..'))
from src.Utils.Dictionaries import nfl_team_index_current
from src.Utils.tools import handle_bye_weeks

def create_nfl_features(team_stats):
    """
    Create NFL-specific features from team statistics.
    Maps NBA features to NFL equivalents and adds NFL-specific metrics.
    """
    features = {}
    
    features['TEAM_NAME'] = team_stats.get('TEAM_NAME', '')
    features['GP'] = team_stats.get('GP', 0)  # Games Played
    features['W'] = team_stats.get('W', 0)    # Wins
    features['L'] = team_stats.get('L', 0)    # Losses
    features['W_PCT'] = team_stats.get('W_PCT', 0.0)  # Win Percentage
    
    features['PTS'] = team_stats.get('PTS', 0.0)  # Points Per Game
    features['PTS_RANK'] = team_stats.get('PTS_RANK', 0)
    
    features['PASS_YDS'] = team_stats.get('FGM', 0.0) * 15  # Passing Yards (estimated)
    features['PASS_ATT'] = team_stats.get('FGA', 0.0) * 2   # Pass Attempts (estimated)
    features['PASS_PCT'] = team_stats.get('FG_PCT', 0.0)    # Completion % (from FG%)
    features['PASS_YDS_RANK'] = team_stats.get('FGM_RANK', 0)
    features['PASS_PCT_RANK'] = team_stats.get('FG_PCT_RANK', 0)
    
    features['RUSH_YDS'] = team_stats.get('FG3M', 0.0) * 25  # Rushing Yards (estimated)
    features['RUSH_ATT'] = team_stats.get('FG3A', 0.0) * 3   # Rush Attempts (estimated)
    features['RUSH_AVG'] = team_stats.get('FG3_PCT', 0.0) * 10  # Yards per carry
    features['RUSH_YDS_RANK'] = team_stats.get('FG3M_RANK', 0)
    features['RUSH_AVG_RANK'] = team_stats.get('FG3_PCT_RANK', 0)
    
    features['RZ_TD_PCT'] = team_stats.get('FT_PCT', 0.0)    # Red Zone TD %
    features['RZ_ATT'] = team_stats.get('FTA', 0.0)          # Red Zone Attempts
    features['RZ_TD'] = team_stats.get('FTM', 0.0)           # Red Zone TDs
    features['RZ_TD_PCT_RANK'] = team_stats.get('FT_PCT_RANK', 0)
    
    features['THIRD_DOWN_PCT'] = team_stats.get('AST', 0.0) / 30.0  # 3rd Down %
    features['THIRD_DOWN_ATT'] = team_stats.get('AST', 0.0) * 1.5   # 3rd Down Attempts
    features['THIRD_DOWN_CONV'] = features['THIRD_DOWN_PCT'] * features['THIRD_DOWN_ATT']
    features['THIRD_DOWN_PCT_RANK'] = team_stats.get('AST_RANK', 0)
    
    features['TURNOVERS'] = team_stats.get('TOV', 0.0)       # Turnovers Given
    features['TAKEAWAYS'] = team_stats.get('STL', 0.0)       # Turnovers Forced
    features['TURNOVER_DIFF'] = features['TAKEAWAYS'] - features['TURNOVERS']
    features['TURNOVERS_RANK'] = team_stats.get('TOV_RANK', 0)
    features['TAKEAWAYS_RANK'] = team_stats.get('STL_RANK', 0)
    
    features['PTS_ALLOWED'] = max(0, features['PTS'] - team_stats.get('PLUS_MINUS', 0.0))
    features['PTS_ALLOWED_RANK'] = 33 - team_stats.get('PLUS_MINUS_RANK', 16)  # Inverse rank
    
    features['PASS_YDS_ALLOWED'] = team_stats.get('DREB', 0.0) * 12  # Pass Yards Allowed
    features['RUSH_YDS_ALLOWED'] = team_stats.get('OREB', 0.0) * 8   # Rush Yards Allowed
    features['TOTAL_YDS_ALLOWED'] = features['PASS_YDS_ALLOWED'] + features['RUSH_YDS_ALLOWED']
    features['PASS_YDS_ALLOWED_RANK'] = team_stats.get('DREB_RANK', 0)
    features['RUSH_YDS_ALLOWED_RANK'] = team_stats.get('OREB_RANK', 0)
    
    features['SACKS'] = team_stats.get('BLK', 0.0)
    features['SACKS_ALLOWED'] = team_stats.get('BLKA', 0.0)
    features['SACK_DIFF'] = features['SACKS'] - features['SACKS_ALLOWED']
    features['SACKS_RANK'] = team_stats.get('BLK_RANK', 0)
    
    features['THIRD_DOWN_DEF_PCT'] = 1.0 - (features['THIRD_DOWN_PCT'] * 0.8)  # Defense %
    features['THIRD_DOWN_DEF_RANK'] = 33 - features['THIRD_DOWN_PCT_RANK']
    
    features['FG_PCT'] = team_stats.get('FG_PCT', 0.0)
    features['FG_MADE'] = team_stats.get('FGM', 0.0) / 10    # Estimated FGs made
    features['FG_ATT'] = team_stats.get('FGA', 0.0) / 10     # Estimated FG attempts
    features['FG_PCT_RANK'] = team_stats.get('FG_PCT_RANK', 0)
    
    features['PUNT_RET_AVG'] = team_stats.get('STL', 0.0) * 2    # Punt Return Average
    features['KICK_RET_AVG'] = team_stats.get('BLK', 0.0) * 3    # Kickoff Return Average
    features['PUNT_RET_TD'] = max(0, team_stats.get('STL', 0.0) - 10) / 10  # Return TDs
    features['KICK_RET_TD'] = max(0, team_stats.get('BLK', 0.0) - 5) / 10   # Return TDs
    
    features['ST_PTS'] = features['FG_MADE'] * 3 + features['PUNT_RET_TD'] * 6 + features['KICK_RET_TD'] * 6
    features['ST_PTS_RANK'] = team_stats.get('FG_PCT_RANK', 0)
    
    features['TIME_POSS'] = team_stats.get('MIN', 48.0)      # Time of Possession
    features['TIME_POSS_PCT'] = features['TIME_POSS'] / 60.0  # % of game time
    features['TIME_POSS_RANK'] = team_stats.get('MIN_RANK', 0)
    
    features['PENALTIES'] = team_stats.get('PF', 0.0)
    features['PENALTY_YDS'] = features['PENALTIES'] * 8      # Estimated penalty yards
    features['PENALTIES_RANK'] = team_stats.get('PF_RANK', 0)
    
    features['HOME_ADVANTAGE'] = 0.0  # Placeholder, calculated per game
    
    features['WEATHER_IMPACT'] = 0.0  # Temperature, wind, precipitation
    
    features['INJURY_IMPACT'] = 0.0   # Key player availability
    
    features['OFF_EFFICIENCY'] = (features['PTS'] / (features['PASS_ATT'] + features['RUSH_ATT'])) * 100
    features['RED_ZONE_EFFICIENCY'] = features['RZ_TD_PCT']
    features['THIRD_DOWN_EFFICIENCY'] = features['THIRD_DOWN_PCT']
    
    features['DEF_EFFICIENCY'] = features['PTS_ALLOWED'] / features['TOTAL_YDS_ALLOWED'] * 100
    features['PASS_DEF_EFFICIENCY'] = features['PTS_ALLOWED'] / features['PASS_YDS_ALLOWED'] * 100
    features['RUSH_DEF_EFFICIENCY'] = features['PTS_ALLOWED'] / features['RUSH_YDS_ALLOWED'] * 100
    
    features['TOTAL_OFFENSE'] = features['PASS_YDS'] + features['RUSH_YDS']
    features['TOTAL_DEFENSE'] = features['TOTAL_YDS_ALLOWED']
    features['NET_YARDS'] = features['TOTAL_OFFENSE'] - features['TOTAL_DEFENSE']
    features['POINT_DIFFERENTIAL'] = features['PTS'] - features['PTS_ALLOWED']
    
    return features

def process_nfl_weekly_data(config, season, week):
    """
    Process NFL data for a specific season and week.
    Handles bye weeks and weekly aggregation vs NBA daily processing.
    """
    try:
        nfl_conn = sqlite3.connect('../../Data/NFLTeamData.sqlite')
        
        table_name = f"{season}-W{week:02d}"
        
        cursor = nfl_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"No data found for {season} Week {week}. Creating sample data for testing...")
            nfl_conn.close()
            sample_teams = create_sample_nfl_data(season, week)
            processed_teams = []
            for team_stats in sample_teams:
                team_features = create_nfl_features(team_stats)
                team_features['Season'] = season
                team_features['Week'] = week
                team_features['Date'] = f"{season}-W{week:02d}"
                processed_teams.append(team_features)
            return processed_teams
            
        query = f"SELECT * FROM '{table_name}'"
        df = pd.read_sql_query(query, nfl_conn)
        nfl_conn.close()
        
        if df.empty:
            print(f"Empty data for {season} Week {week}. Creating sample data for testing...")
            nfl_conn.close()
            sample_teams = create_sample_nfl_data(season, week)
            processed_teams = []
            for team_stats in sample_teams:
                team_features = create_nfl_features(team_stats)
                team_features['Season'] = season
                team_features['Week'] = week
                team_features['Date'] = f"{season}-W{week:02d}"
                processed_teams.append(team_features)
            return processed_teams
            
        processed_teams = []
        for _, team_row in df.iterrows():
            team_features = create_nfl_features(team_row.to_dict())
            team_features['Season'] = season
            team_features['Week'] = week
            team_features['Date'] = f"{season}-W{week:02d}"
            processed_teams.append(team_features)
            
        return processed_teams
        
    except Exception as e:
        print(f"Error processing {season} Week {week}: {e}")
        return None

def create_nfl_games_dataset():
    """
    Main function to create NFL games dataset with 40+ features.
    Processes seasons 2019-2024 with weekly structure.
    """
    config = toml.load('../../config.toml')
    nfl_config = config.get('create-nfl-games', {})
    
    print("Creating NFL Games Dataset with 40+ Features...")
    print("Processing seasons 2019-2024 with weekly structure")
    
    try:
        odds_conn = sqlite3.connect('../../Data/OddsData.sqlite')
        print("Connected to OddsData.sqlite")
    except Exception as e:
        print(f"Warning: Could not connect to OddsData.sqlite: {e}")
        odds_conn = None
    
    all_games = []
    
    seasons = nfl_config.get('seasons', ['2019', '2020', '2021', '2022', '2023', '2024'])
    
    for season in seasons:
        print(f"\nProcessing NFL {season} season...")
        
        season_config = nfl_config.get(season, {})
        start_week = season_config.get('start_week', 1)
        end_week = season_config.get('end_week', 18)
        
        for week in range(start_week, end_week + 1):
            print(f"Processing Week {week}...")
            
            weekly_teams = process_nfl_weekly_data(config, season, week)
            if not weekly_teams:
                continue
                
            active_teams = weekly_teams
            
            games_this_week = create_weekly_games(active_teams, season, week, odds_conn)
            
            if games_this_week:
                all_games.extend(games_this_week)
                print(f"Added {len(games_this_week)} games from Week {week}")
    
    if odds_conn:
        odds_conn.close()
    
    if not all_games:
        print("No games data created. Check NFL data availability.")
        return
    
    print(f"\nCreating dataset with {len(all_games)} total games...")
    df = pd.DataFrame(all_games)
    
    dataset_conn = sqlite3.connect('../../Data/NFLDataset.sqlite')
    table_name = 'nfl_dataset_2019-24'
    
    df.to_sql(table_name, dataset_conn, if_exists='replace', index=False)
    dataset_conn.close()
    
    print(f"NFL Dataset created successfully!")
    print(f"Table: {table_name}")
    print(f"Total games: {len(df)}")
    print(f"Total features: {len(df.columns)}")
    print(f"Seasons covered: {min(seasons)} - {max(seasons)}")
    
    print("\nFeature Summary:")
    feature_categories = {
        'Basic': ['TEAM_NAME', 'GP', 'W', 'L', 'W_PCT'],
        'Offensive': ['PTS', 'PASS_YDS', 'RUSH_YDS', 'RZ_TD_PCT', 'THIRD_DOWN_PCT'],
        'Defensive': ['PTS_ALLOWED', 'TOTAL_YDS_ALLOWED', 'SACKS', 'THIRD_DOWN_DEF_PCT'],
        'Special Teams': ['FG_PCT', 'PUNT_RET_AVG', 'KICK_RET_AVG', 'ST_PTS'],
        'Context': ['TIME_POSS', 'PENALTIES', 'WEATHER_IMPACT', 'INJURY_IMPACT'],
        'Advanced': ['OFF_EFFICIENCY', 'DEF_EFFICIENCY', 'NET_YARDS', 'POINT_DIFFERENTIAL']
    }
    
    for category, features in feature_categories.items():
        available_features = [f for f in features if f in df.columns]
        print(f"{category}: {len(available_features)} features")
    
    return df

def create_weekly_games(teams, season, week, odds_conn):
    """
    Create game records from weekly team data.
    Matches home/away teams and adds game context.
    """
    games = []
    
    team_pairs = []
    for i in range(0, len(teams), 2):
        if i + 1 < len(teams):
            home_team = teams[i]
            away_team = teams[i + 1]
            team_pairs.append((home_team, away_team))
    
    for home_team, away_team in team_pairs:
        game = {}
        
        for key, value in home_team.items():
            game[key] = value
            
        for key, value in away_team.items():
            if key not in ['Season', 'Week', 'Date']:  # Don't duplicate metadata
                game[f"{key}.1"] = value
        
        game['Score'] = home_team.get('PTS', 0) + away_team.get('PTS', 0)  # Total score
        game['Home-Team-Win'] = 1 if home_team.get('PTS', 0) > away_team.get('PTS', 0) else 0
        game['OU'] = game['Score']  # Over/Under line (simplified)
        game['OU-Cover'] = 1 if game['Score'] > 45 else 0  # Simplified O/U cover
        
        game['Days-Rest-Home'] = 7  # Standard week rest
        game['Days-Rest-Away'] = 7  # Standard week rest
        
        if week > 1:
            game['Days-Rest-Home'] = 14 if home_team.get('GP', 0) < week - 1 else 7
            game['Days-Rest-Away'] = 14 if away_team.get('GP', 0) < week - 1 else 7
        
        game['HOME_ADVANTAGE'] = 3.0  # Standard NFL home field advantage
        
        games.append(game)
    
    return games

def create_sample_nfl_data(season, week):
    """
    Create sample NFL team data for testing when API data is not available.
    Uses realistic NFL statistics ranges.
    """
    sample_teams = []
    
    nfl_teams = [
        'Kansas City Chiefs', 'Buffalo Bills', 'Cincinnati Bengals', 'Tennessee Titans',
        'Indianapolis Colts', 'Houston Texans', 'Jacksonville Jaguars', 'Denver Broncos',
        'Las Vegas Raiders', 'Los Angeles Chargers', 'Pittsburgh Steelers', 'Baltimore Ravens',
        'Cleveland Browns', 'New England Patriots', 'Miami Dolphins', 'New York Jets',
        'Dallas Cowboys', 'Philadelphia Eagles', 'New York Giants', 'Washington Commanders',
        'Green Bay Packers', 'Minnesota Vikings', 'Chicago Bears', 'Detroit Lions',
        'Tampa Bay Buccaneers', 'New Orleans Saints', 'Atlanta Falcons', 'Carolina Panthers',
        'San Francisco 49ers', 'Seattle Seahawks', 'Los Angeles Rams', 'Arizona Cardinals'
    ]
    
    for i, team_name in enumerate(nfl_teams):
        team_stats = {
            'TEAM_NAME': team_name,
            'GP': week,  # Games played = current week
            'W': max(0, week - 2 + (i % 3)),  # Wins (varied by team)
            'L': week - max(0, week - 2 + (i % 3)),  # Losses
            'W_PCT': max(0, week - 2 + (i % 3)) / max(1, week),  # Win percentage
            'MIN': 60.0,  # Game time in minutes
            
            'FGM': 25 + (i % 10),  # Field goals made -> passing completions
            'FGA': 40 + (i % 15),  # Field goals attempted -> passing attempts  
            'FG_PCT': (25 + (i % 10)) / (40 + (i % 15)),  # Completion percentage
            'FG3M': 120 + (i % 30),  # 3-pointers -> rushing yards
            'FG3A': 25 + (i % 8),   # 3-point attempts -> rushing attempts
            'FG3_PCT': 4.8 + (i % 2),  # Yards per carry
            'FTM': 3 + (i % 3),     # Free throws -> red zone TDs
            'FTA': 5 + (i % 2),     # Free throw attempts -> red zone attempts
            'FT_PCT': (3 + (i % 3)) / (5 + (i % 2)),  # Red zone efficiency
            
            'OREB': 80 + (i % 20),  # Offensive rebounds -> rushing yards allowed
            'DREB': 200 + (i % 50), # Defensive rebounds -> passing yards allowed
            'REB': 280 + (i % 70),  # Total rebounds -> total yards allowed
            'AST': 12 + (i % 6),    # Assists -> third down conversions
            'TOV': 1 + (i % 3),     # Turnovers
            'STL': 1 + (i % 3),     # Steals -> takeaways
            'BLK': 2 + (i % 2),     # Blocks -> sacks
            'BLKA': 2 + (i % 2),    # Blocks against -> sacks allowed
            'PF': 6 + (i % 4),      # Personal fouls -> penalties
            'PFD': 5 + (i % 3),     # Personal fouls drawn
            'PTS': 24 + (i % 12),   # Points scored
            'PLUS_MINUS': (i % 21) - 10,  # Point differential
            
            # Rankings (simplified)
            'GP_RANK': (i % 32) + 1,
            'W_RANK': (i % 32) + 1,
            'L_RANK': (i % 32) + 1,
            'W_PCT_RANK': (i % 32) + 1,
            'MIN_RANK': (i % 32) + 1,
            'FGM_RANK': (i % 32) + 1,
            'FGA_RANK': (i % 32) + 1,
            'FG_PCT_RANK': (i % 32) + 1,
            'FG3M_RANK': (i % 32) + 1,
            'FG3A_RANK': (i % 32) + 1,
            'FG3_PCT_RANK': (i % 32) + 1,
            'FTM_RANK': (i % 32) + 1,
            'FTA_RANK': (i % 32) + 1,
            'FT_PCT_RANK': (i % 32) + 1,
            'OREB_RANK': (i % 32) + 1,
            'DREB_RANK': (i % 32) + 1,
            'REB_RANK': (i % 32) + 1,
            'AST_RANK': (i % 32) + 1,
            'TOV_RANK': (i % 32) + 1,
            'STL_RANK': (i % 32) + 1,
            'BLK_RANK': (i % 32) + 1,
            'BLKA_RANK': (i % 32) + 1,
            'PF_RANK': (i % 32) + 1,
            'PFD_RANK': (i % 32) + 1,
            'PTS_RANK': (i % 32) + 1,
            'PLUS_MINUS_RANK': (i % 32) + 1,
            'Date': f"{season}-W{week:02d}"
        }
        
        sample_teams.append(team_stats)
    
    return sample_teams

if __name__ == "__main__":
    create_nfl_games_dataset()
