#!/usr/bin/env python3
"""Test script to verify API key reading functionality"""

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '.'))
from src.Utils.api_keys import get_nfl_api_key

def test_api_key_reading():
    print('Testing API key reading...')
    key = get_nfl_api_key()
    if key:
        print(f'✅ Successfully read API key: {key[:10]}...')
        return True
    else:
        print('❌ Failed to read API key')
        return False

if __name__ == "__main__":
    success = test_api_key_reading()
    sys.exit(0 if success else 1)
