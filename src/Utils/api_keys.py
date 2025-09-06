import os
from pathlib import Path

def get_api_key_from_file(key_name, filename="api_keys.txt"):
    """
    Read API key from a file in the project root directory.
    
    Args:
        key_name (str): Name of the API key to retrieve
        filename (str): Name of the file containing API keys
        
    Returns:
        str: API key value or None if not found
    """
    project_root = Path(__file__).parent.parent.parent
    key_file_path = project_root / filename
    
    if not key_file_path.exists():
        print(f"Warning: API key file '{filename}' not found at {key_file_path}")
        return None
    
    try:
        with open(key_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        name, value = line.split('=', 1)
                        if name.strip() == key_name:
                            return value.strip()
    except Exception as e:
        print(f"Error reading API key file: {e}")
        return None
    
    print(f"Warning: API key '{key_name}' not found in {filename}")
    return None

def get_nfl_api_key():
    """
    Get the NFL API key from file, with fallback to environment variable.
    
    Returns:
        str: NFL API key or None if not found
    """
    api_key = get_api_key_from_file('NFL_API_KEY')
    
    if not api_key:
        api_key = os.getenv('NFL_API_KEY')
        if api_key:
            print("Using NFL_API_KEY from environment variable")
    
    if not api_key:
        print("Warning: NFL_API_KEY not found in file or environment variable. API calls may fail.")
    
    return api_key
