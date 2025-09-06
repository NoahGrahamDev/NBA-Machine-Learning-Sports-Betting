# TheSportsDB Migration Notes

## What Changed

### API Migration
- **From**: sportsdata.io (subscription required, API key needed)
- **To**: TheSportsDB (completely free, no API key required)

### Key Changes Made

1. **Updated `src/Utils/tools.py`**:
   - Added `get_nfl_json_data_thesportsdb()` function
   - Added `to_nfl_data_frame_thesportsdb()` function
   - Kept legacy functions for backward compatibility

2. **Updated `src/Process-Data/Get_Data.py`**:
   - Removed API key dependency
   - Changed from week-by-week fetching to season-based fetching
   - Updated to use TheSportsDB functions

3. **Updated `config.toml`**:
   - Added TheSportsDB endpoint configurations
   - Kept legacy sportsdata.io URLs for reference

4. **Added test script**: `test_thesportsdb_migration.py`

### Data Structure Mapping

| sportsdata.io Field | TheSportsDB Field | Mapped Field |
|-------------------|------------------|--------------|
| GameKey | idEvent | GameKey |
| Season | strSeason | Season |
| Date | dateEvent | Date |
| HomeTeam | strHomeTeam | HomeTeam |
| AwayTeam | strAwayTeam | AwayTeam |
| HomeScore | intHomeScore | HomeScore |
| AwayScore | intAwayScore | AwayScore |
| - | idHomeTeam | HomeTeamID |
| - | idAwayTeam | AwayTeamID |

### Benefits of Migration

1. **No subscription costs**: TheSportsDB is completely free
2. **No API key management**: Uses public test key "123"
3. **Historical data access**: Full access to 2019-2024 seasons
4. **Rate limiting**: 30 requests/minute (sufficient for batch processing)
5. **Reliable service**: 9+ years of operation

### Testing

Run the migration test:
```bash
python test_thesportsdb_migration.py
```

This will verify:
- API connectivity for all required seasons (2019-2024)
- Data retrieval and formatting
- DataFrame conversion
- Sample data display

### Backward Compatibility

The migration maintains backward compatibility by:
- Keeping legacy functions with deprecation warnings
- Preserving the same database schema
- Maintaining similar data structure in DataFrames

### Rate Limiting

TheSportsDB free tier allows:
- 30 requests per minute
- For 6 seasons: only 6 requests total needed
- Added 2-second delay between requests for safety
