#!/usr/bin/env python3
"""Test script to verify TheSportsDB migration works correctly"""

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '.'))
from src.Utils.tools import get_nfl_json_data_thesportsdb, to_nfl_data_frame_thesportsdb

def test_thesportsdb_migration():
    """Test TheSportsDB API integration"""
    print("=== Testing TheSportsDB Migration ===")
    
    test_seasons = [2019, 2020, 2021, 2022, 2023, 2024]
    
    for season in test_seasons:
        print(f"\n--- Testing Season {season} ---")
        
        json_data = get_nfl_json_data_thesportsdb(season)
        
        if json_data:
            print(f"✅ API call successful: {len(json_data)} games retrieved")
            
            df = to_nfl_data_frame_thesportsdb(json_data)
            
            if not df.empty:
                print(f"✅ DataFrame conversion successful: {len(df)} rows")
                print(f"   Columns: {list(df.columns)}")
                
                if len(df) > 0:
                    sample = df.iloc[0]
                    print(f"   Sample game: {sample['AwayTeam']} @ {sample['HomeTeam']} ({sample['AwayScore']}-{sample['HomeScore']})")
            else:
                print("❌ DataFrame conversion failed: empty DataFrame")
        else:
            print("❌ API call failed: no data retrieved")
    
    print("\n=== Migration Test Complete ===")

if __name__ == "__main__":
    test_thesportsdb_migration()
