#!/usr/bin/env python3

import sqlite3
import pandas as pd

def inspect_nfl_dataset():
    """Inspect the NFLDataset.sqlite structure"""
    print("Inspecting NFLDataset.sqlite structure...")
    
    try:
        con = sqlite3.connect('Data/NFLDataset.sqlite')
        cursor = con.cursor()
        
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print(f"Tables found: {tables}")
        
        for table_name in tables:
            table = table_name[0]
            print(f"\n--- Table: {table} ---")
            
            cursor.execute(f'PRAGMA table_info("{table}")')
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            total_rows = cursor.fetchone()[0]
            print(f"Total rows: {total_rows}")
            
            df = pd.read_sql_query(f'SELECT * FROM "{table}" LIMIT 1', con)
            print(f"DataFrame columns: {list(df.columns)}")
            
            key_columns = ['Home-Team-Win', 'OU-Cover', 'Score', 'TEAM_NAME']
            found_columns = []
            for key_col in key_columns:
                if key_col in df.columns:
                    found_columns.append(key_col)
            print(f"Key columns found: {found_columns}")
        
        con.close()
        print("\nInspection complete!")
        
    except Exception as e:
        print(f"Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_nfl_dataset()
