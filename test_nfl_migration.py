#!/usr/bin/env python3

import os
import sys
import toml
import importlib.util

def test_config_file():
    """Test that config.toml is valid and contains NFL endpoints"""
    print("Testing config.toml...")
    try:
        config = toml.load("config.toml")
        
        required_keys = ['nfl_api_base_url', 'nfl_teams_url', 'nfl_standings_url', 
                        'nfl_schedules_url', 'nfl_scores_url', 'nfl_team_stats_url']
        
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing NFL API endpoint: {key}")
                return False
            print(f"✅ Found NFL API endpoint: {key}")
        
        if 'get-nfl-data' not in config:
            print("❌ Missing get-nfl-data section")
            return False
        print("✅ Found get-nfl-data section")
        
        if 'get-nfl-odds-data' not in config:
            print("❌ Missing get-nfl-odds-data section")
            return False
        print("✅ Found get-nfl-odds-data section")
        
        print("✅ config.toml validation passed")
        return True
        
    except Exception as e:
        print(f"❌ config.toml validation failed: {e}")
        return False

def test_dictionaries():
    """Test that Dictionaries.py contains NFL team mappings"""
    print("\nTesting Dictionaries.py...")
    try:
        sys.path.insert(0, 'src/Utils')
        from Dictionaries import nfl_team_codes, nfl_team_index_current
        
        if len(nfl_team_codes) != 32:
            print(f"❌ Expected 32 NFL teams, found {len(nfl_team_codes)}")
            return False
        print(f"✅ Found {len(nfl_team_codes)} NFL teams")
        
        if len(nfl_team_index_current) != 32:
            print(f"❌ Expected 32 NFL team indices, found {len(nfl_team_index_current)}")
            return False
        print(f"✅ Found {len(nfl_team_index_current)} NFL team indices")
        
        key_teams = ['Kansas City Chiefs', 'Buffalo Bills', 'San Francisco 49ers', 'Dallas Cowboys']
        for team in key_teams:
            if team not in nfl_team_index_current:
                print(f"❌ Missing key NFL team: {team}")
                return False
            print(f"✅ Found key NFL team: {team}")
        
        print("✅ Dictionaries.py validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Dictionaries.py validation failed: {e}")
        return False

def test_tools():
    """Test that tools.py contains NFL functions"""
    print("\nTesting tools.py...")
    try:
        sys.path.insert(0, 'src/Utils')
        from tools import get_nfl_json_data, to_nfl_data_frame, get_nfl_current_week, handle_bye_weeks
        
        print("✅ Found get_nfl_json_data function")
        print("✅ Found to_nfl_data_frame function")
        print("✅ Found get_nfl_current_week function")
        print("✅ Found handle_bye_weeks function")
        
        current_week = get_nfl_current_week()
        if not (1 <= current_week <= 18):
            print(f"❌ Invalid current week: {current_week}")
            return False
        print(f"✅ Current NFL week calculation: {current_week}")
        
        is_bye = handle_bye_weeks('Kansas City Chiefs', 6, 2024)
        print(f"✅ Bye week handling test: KC Chiefs week 6 2024 = {is_bye}")
        
        print("✅ tools.py validation passed")
        return True
        
    except Exception as e:
        print(f"❌ tools.py validation failed: {e}")
        return False

def test_data_scripts():
    """Test that data collection scripts can be imported"""
    print("\nTesting data collection scripts...")
    try:
        spec = importlib.util.spec_from_file_location("get_data", "src/Process-Data/Get_Data.py")
        if spec is None:
            print("❌ Could not load Get_Data.py")
            return False
        print("✅ Get_Data.py syntax valid")
        
        spec = importlib.util.spec_from_file_location("get_odds_data", "src/Process-Data/Get_Odds_Data.py")
        if spec is None:
            print("❌ Could not load Get_Odds_Data.py")
            return False
        print("✅ Get_Odds_Data.py syntax valid")
        
        print("✅ Data collection scripts validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Data collection scripts validation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏈 NFL Migration Phase 1 Validation Tests")
    print("=" * 50)
    
    tests = [
        test_config_file,
        test_dictionaries,
        test_tools,
        test_data_scripts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Phase 1 migration tests passed!")
        print("\nNext steps:")
        print("1. Set NFL_API_KEY environment variable")
        print("2. Test data collection with: python src/Process-Data/Get_Data.py")
        print("3. Test odds collection with: python src/Process-Data/Get_Odds_Data.py")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
