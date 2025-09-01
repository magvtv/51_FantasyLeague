# NFL Fantasy League CLI - Data Management

This document describes the data management commands for the NFL Fantasy League CLI application.

## Overview

The data management system has been updated to use real NFL data from RapidAPI instead of generating sample data. This provides accurate historical statistics for the 2024 season and current injury information.

## Available Commands

### 1. Import NFL Player Data
```bash
python cli.py data import-nfl-data [OPTIONS]
```

**Options:**
- `--teams INTEGER`: Number of teams to import (default: 5)
- `--force`: Force reimport even if data exists

**Description:** Imports basic player information (name, position, team) from the NFL API.

### 2. Import Historical Scores
```bash
python cli.py data import-historical-scores [OPTIONS]
```

**Options:**
- `--weeks INTEGER`: Number of weeks to import (default: 18 for full season)
- `--season INTEGER`: Season to import data for (default: 2024)
- `--force`: Force reimport even if data exists

**Description:** Imports weekly fantasy scores from the 2024 season. This provides historical performance data for all players.

### 3. Import Season Statistics
```bash
python cli.py data import-season-stats [OPTIONS]
```

**Options:**
- `--season INTEGER`: Season to import data for (default: 2024)
- `--force`: Force reimport even if data exists

**Description:** Imports season-long statistics and calculates total fantasy points for all players.

### 4. Import Injury Data
```bash
python cli.py data import-injury-data [OPTIONS]
```

**Options:**
- `--force`: Force reimport even if data exists

**Description:** Imports current injury status for all players. Updates the `is_injured` and `injury_status` fields.

### 5. List Commands
```bash
python cli.py data list-commands
```

**Description:** Shows a help message with all available data management commands.

## Setup Instructions

### 1. Environment Configuration
Make sure you have the following environment variables set in your `.env` file:

```env
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=nfl-api-data.p.rapidapi.com
```

### 2. Database Setup
Ensure your database is initialized:

```bash
python cli.py db init
```

### 3. Data Import Workflow
Follow this recommended order for importing data:

1. **Import basic player data:**
   ```bash
   python cli.py data import-nfl-data --teams 32
   ```

2. **Import historical scores:**
   ```bash
   python cli.py data import-historical-scores --weeks 18 --season 2024
   ```

3. **Import season statistics:**
   ```bash
   python cli.py data import-season-stats --season 2024
   ```

4. **Import current injury data:**
   ```bash
   python cli.py data import-injury-data
   ```

## API Endpoints Used

The system uses the following RapidAPI endpoints:

- **Teams:** `nfl-team-listing/v1/data`
- **Players:** `nfl-team-roster/v1/data`
- **Season Stats:** `nfl-season-stats/v1/data`
- **Weekly Stats:** `nfl-weekly-stats/v1/data`
- **Injury Report:** `nfl-injury-report/v1/data`

## Data Processing

### Fantasy Points Calculation
The system calculates fantasy points using PPR (Point Per Reception) scoring:

- **Passing:** 1 point per 25 yards, 4 points per TD, -2 points per interception
- **Rushing:** 1 point per 10 yards, 6 points per TD
- **Receiving:** 1 point per 10 yards, 6 points per TD, 1 point per reception
- **Fumbles:** -2 points per fumble
- **Kicking:** 3 points per field goal, 1 point per extra point
- **Defense:** 6 points per TD, 2 points per interception, points allowed bonuses

### Position-Specific Stats
Different statistics are tracked based on player position:

- **QB:** Passing yards, TDs, interceptions, rushing yards, TDs
- **RB:** Rushing yards, TDs, receiving yards, TDs, receptions
- **WR:** Receiving yards, TDs, receptions
- **TE:** Receiving yards, TDs, receptions
- **K:** Field goals made, extra points made
- **DEF:** Defensive TDs, interceptions, points allowed

## Testing

Run the API endpoint test script to verify connectivity:

```bash
python test_api_endpoints.py
```

This will test all major endpoints and report their status.

## Error Handling

The system includes comprehensive error handling:

- **API Key Validation:** Checks for valid RapidAPI key before making requests
- **Data Validation:** Ensures API responses contain expected data structures
- **Graceful Degradation:** Continues processing even if some players don't have data
- **Progress Tracking:** Shows progress bars for long-running operations

## Troubleshooting

### Common Issues

1. **"RAPIDAPI_KEY not found"**
   - Ensure your `.env` file contains the correct API key
   - Check that the key is valid and has sufficient credits

2. **"No players found in database"**
   - Run `import-nfl-data` first to populate the player database

3. **"No stats found for Week X"**
   - Some weeks may not have complete data available
   - The system will skip weeks with missing data

4. **API Rate Limiting**
   - The system includes caching to reduce API calls
   - If you hit rate limits, wait a few minutes and retry

### Performance Tips

- Use the `--force` flag sparingly to avoid unnecessary API calls
- The system caches API responses for 5 minutes
- Consider running imports during off-peak hours

## Future Enhancements

Planned improvements include:

- Real-time score updates during live games
- Player projections and rankings
- Team depth chart information
- Advanced analytics and trends
- Export functionality for external analysis

