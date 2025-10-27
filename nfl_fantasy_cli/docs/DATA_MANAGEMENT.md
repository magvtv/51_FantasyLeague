# NFL Fantasy League CLI - Data Management

This document describes the data management commands for the NFL Fantasy League CLI application with real NFL API integration.

## Overview

The data management system has been completely updated to use **real NFL data** from RapidAPI instead of generating sample data. This provides accurate live scores, player details, team rosters, injury reports, and statistics for the current NFL season.

## Available Commands

### 1. Live NFL Data Access
```bash
# Get live game scores
python3 cli.py api live-scores

# Get NFL calendar/schedule
python3 cli.py api calendar

# Get player details
python3 cli.py api player-detail --player-id 4360644

# Get player statistics
python3 cli.py api player-stats --player-id 15035 --year 2023

# Get team roster
python3 cli.py api team-roster --team-id 22

# Get team injuries
python3 cli.py api team-injuries --team-id 22

# Get team statistics
python3 cli.py api team-statistics --team-id 22 --year 2023

# Get coach details
python3 cli.py api coach-details --coach-id 17587
```

### 2. Data Analysis Commands
```bash
# Analyze player for fantasy value
python3 cli.py api analyze-player --player-id 4360644

# Analyze team performance
python3 cli.py api analyze-team --team-id 22

# Get current game status
python3 cli.py api game-status
```

### 3. Data Synchronization Commands
```bash
# Sync live scores to database
python3 cli.py api sync-live-scores

# Sync player details to database
python3 cli.py api sync-player-details --player-id 4360644

# Sync team injuries to database
python3 cli.py api sync-team-injuries --team-id 22

# Sync all team rosters
python3 cli.py api sync-all-rosters

# Sync all team injuries
python3 cli.py api sync-all-injuries
```

### 4. Legacy Import Commands (Deprecated)
```bash
# These commands are now deprecated in favor of real API data
python3 cli.py data import-nfl-data [OPTIONS]
python3 cli.py data import-historical-scores [OPTIONS]
python3 cli.py data import-season-stats [OPTIONS]
python3 cli.py data import-injury-data [OPTIONS]
```

## Setup Instructions

### 1. Environment Configuration
Make sure you have the following environment variables set in your `.env` file:

```env
# NFL API Configuration (RapidAPI)
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=nfl-api-data.p.rapidapi.com

# Database Configuration
SUPABASE_DB_URL=postgresql://user:password@host:port/database
# OR for development
DATABASE_URL=sqlite:///instance/nfl_fantasy.db
```

### 2. Database Setup
Ensure your database is initialized:

```bash
# For SQLite (development)
bash setup_sqlite.sh

# For Supabase PostgreSQL (production)
bash setup_modular_teams.sh
```

### 3. Test API Integration
```bash
# Test real NFL API data
python3 tools/integration/nfl_fantasy_parsers.py

# Run CLI demo
python3 tools/demos/real_data_cli_demo.py

# Analyze JSON structures
python3 tools/analysis/analyze_json_structure_fixed.py
```

## API Endpoints Used

The system uses the following RapidAPI endpoints for real NFL data:

### **Live Data**
- **Live Scores:** `nfl-livescores` - Real-time game scores and status
- **NFL Calendar:** `nfl-ondays` - Complete schedule and event dates

### **Player Data**
- **Player Details:** `nfl-player-info/v1/data` - Complete player information
- **Player Statistics:** `nfl-ath-statistics` - Performance data by year
- **Player Overview:** `nfl-ath-overview` - Player summary and stats
- **Player Standings:** `nfl-ath-standings` - Player rankings

### **Team Data**
- **Team Rosters:** `nfl-team-roster` - Complete team rosters (87 players)
- **Team Injuries:** `nfl-team-injuries` - Detailed injury reports
- **Team Statistics:** `nfl-team-statistics` - Team performance data
- **Coach Details:** `nfl-single-coaches` - Coach information

## Data Processing

### **Structured JSON Parsing**
The system uses specialized parsers (`tools/integration/nfl_fantasy_parsers.py`) to extract fantasy-relevant data from complex NFL API responses:

- **Live Scores:** Game status, team scores, winners
- **Player Details:** Name, position, physical stats, experience
- **Team Rosters:** 87 players per team, position filtering
- **Injury Reports:** Status updates, detailed comments
- **Statistics:** Performance data by year/week

### **Fantasy Points Calculation**
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

### **API Integration Tests**
```bash
# Test all NFL API endpoints
python3 tools/integration/nfl_fantasy_parsers.py

# Test CLI commands with real data
python3 tools/demos/real_data_cli_demo.py

# Analyze JSON response structures
python3 tools/analysis/analyze_json_structure_fixed.py
```

### **Manual Testing**
```bash
# Test live scores
python3 cli.py api live-scores

# Test player data
python3 cli.py api player-detail --player-id 4360644

# Test team data
python3 cli.py api team-roster --team-id 22
```

## Error Handling

The system includes comprehensive error handling for real NFL API data:

- **API Key Validation:** Checks for valid RapidAPI key before making requests
- **Data Structure Validation:** Handles varying JSON response structures
- **Graceful Degradation:** Continues processing even if some data is missing
- **Progress Tracking:** Shows progress bars for long-running operations
- **Caching:** Reduces API calls with intelligent caching
- **Rate Limiting:** Respects API rate limits and quotas

## Troubleshooting

### Common Issues

1. **"RAPIDAPI_KEY not found"**
   - Ensure your `.env` file contains the correct API key
   - Check that the key is valid and has sufficient credits

2. **"No data returned from API"**
   - Some endpoints may not have data for certain players/teams
   - The system will handle missing data gracefully

3. **"API Rate Limiting"**
   - The system includes caching to reduce API calls
   - If you hit rate limits, wait a few minutes and retry

4. **"JSON parsing errors"**
   - Use the analysis tools to understand data structures
   - Check `tools/analysis/analyze_json_structure_fixed.py`

### Performance Tips

- The system caches API responses for 5 minutes
- Use the `--force` flag sparingly to avoid unnecessary API calls
- Consider running imports during off-peak hours
- Use the development tools to test data structures before integration

## Future Enhancements

Planned improvements include:

- **Real-time score updates** during live games
- **Player projections** and rankings based on real data
- **Team depth chart** information from rosters
- **Advanced analytics** and trends from statistics
- **Export functionality** for external analysis
- **Webhook integration** for real-time notifications
- **Machine learning** for fantasy predictions

## Development Tools

### **Analysis Tools** (`tools/analysis/`)
- JSON structure analysis
- Data format understanding
- API response debugging

### **Integration Tools** (`tools/integration/`)
- Structured data parsers
- Fantasy league integration examples
- Working data processors

### **Demo Tools** (`tools/demos/`)
- CLI demonstrations with real data
- Usage examples and tutorials

---

**The NFL Fantasy League CLI now provides real, live NFL data for accurate fantasy league management!** 🏈✨

