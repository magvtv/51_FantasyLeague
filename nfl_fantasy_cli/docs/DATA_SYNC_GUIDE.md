# Data Synchronization Guide

## Overview

Your NFL Fantasy League application now has a complete data synchronization system that bridges the external NFL API with your Supabase database. This allows you to:

1. **Fetch live data** from the NFL API
2. **Store it in Supabase** for fantasy league use
3. **Query your database** for fantasy league operations
4. **Keep data fresh** with regular synchronization

## How It Works

### 1. **Data Flow**
```
NFL API → Data Sync Service → Supabase Database → Your Fantasy League App
```

### 2. **Components**
- **`data_sync_service.py`**: Core synchronization logic
- **`sync_data.py`**: CLI interface for running syncs
- **Enhanced `api_service.py`**: Database-aware API methods

## Usage

### **Full Data Synchronization**
```bash
# Sync everything: teams, players, stats, injuries
python sync_data.py --full
```

### **Individual Sync Operations**
```bash
# Sync only NFL teams
python sync_data.py --teams

# Sync only NFL players
python sync_data.py --players

# Sync player statistics for current season
python sync_data.py --stats

# Sync injury data
python sync_data.py --injuries

# Sync stats for specific week
python sync_data.py --stats --week 5

# Sync players for specific team
python sync_data.py --players --team-id 16
```

### **Help and Options**
```bash
python sync_data.py --help
```

## What Gets Synced

### **NFL Teams**
- Team names, abbreviations, locations
- Currently logged to console (you can add a teams table later)

### **NFL Players**
- Player names, positions, teams
- Stored in `nfl_players` table
- Includes fantasy pricing and injury status

### **Player Statistics**
- Weekly and season stats
- Stored in `weekly_scores` table
- Automatic fantasy point calculation
- Supports passing, rushing, receiving stats

### **Injury Data**
- Player injury status
- Updates `nfl_players` table
- Tracks injury status and details

## Database Integration

### **New API Methods**

Your `api_service.py` now includes database-aware methods:

```python
# Get players from your database (not external API)
nfl_api.get_fantasy_players_from_db(position='QB', team='KC')

# Get player fantasy stats from database
nfl_api.get_player_fantasy_stats(player_id=123, season=2024, week=5)

# Get fantasy rankings from database
nfl_api.get_fantasy_rankings_from_db(position='RB', season=2024)

# Get injured players from database
nfl_api.get_injured_players_from_db()
```

### **Data Sources**

- **External API**: Live NFL data (teams, players, stats)
- **Database**: Fantasy league data (user teams, lineups, transfers)
- **Hybrid**: Some methods fall back to API if database unavailable

## Fantasy Point Calculation

The system automatically calculates fantasy points based on:

- **Passing**: 1 point per 25 yards, 4 points per TD, -2 points per INT
- **Rushing**: 1 point per 10 yards, 6 points per TD
- **Receiving**: 1 point per 10 yards, 6 points per TD, 0.5 points per reception
- **Penalties**: -2 points per fumble

## Scheduling Regular Syncs

### **Manual Sync**
```bash
# Run when you need fresh data
python sync_data.py --full
```

### **Automated Sync (Recommended)**
```bash
# Add to crontab for daily sync at 6 AM
0 6 * * * cd /path/to/nfl_fantasy_cli && python sync_data.py --full

# Or sync specific data types at different times
0 6 * * * cd /path/to/nfl_fantasy_cli && python sync_data.py --players --stats
0 8 * * * cd /path/to/nfl_fantasy_cli && python sync_data.py --injuries
```

## Example Workflow

### **1. Initial Setup**
```bash
# First time: sync all data
python sync_data.py --full
```

### **2. Daily Operations**
```bash
# Morning: sync fresh stats and injuries
python sync_data.py --stats --injuries

# Your fantasy league app now has current data
```

### **3. Weekly Updates**
```bash
# After each game week: sync new stats
python sync_data.py --stats --week 6
```

## Troubleshooting

### **Common Issues**

1. **API Rate Limits**
   - NFL API has rate limits
   - Sync may take time for large datasets
   - Consider breaking syncs into smaller chunks

2. **Database Connection**
   - Ensure Supabase credentials are correct
   - Check IP whitelist in Supabase dashboard
   - Verify database tables exist

3. **Data Quality**
   - Some API endpoints may return incomplete data
   - System gracefully handles missing fields
   - Check console output for warnings

### **Debug Mode**
```bash
# Run with verbose output
python sync_data.py --full 2>&1 | tee sync.log
```

## Performance Tips

1. **Incremental Syncs**: Use `--week` flag for specific weeks
2. **Team-Specific**: Use `--team-id` for specific teams
3. **Scheduled Syncs**: Run during off-peak hours
4. **Monitor Logs**: Check for failed syncs and retry

## Next Steps

1. **Run initial sync**: `python sync_data.py --full`
2. **Test database methods**: Use the new API methods in your app
3. **Set up scheduling**: Configure automated syncs
4. **Monitor performance**: Track sync success rates
5. **Customize scoring**: Modify fantasy point calculations if needed

## Benefits

✅ **Live Data**: Always current NFL information  
✅ **Fantasy Focused**: Data structured for fantasy league use  
✅ **Hybrid Approach**: Combines external API with local database  
✅ **Automated**: Can run unattended with scheduling  
✅ **Flexible**: Sync specific data types as needed  
✅ **Scalable**: Handles large datasets efficiently  

Your fantasy league application now has access to both live NFL data and persistent fantasy league data, giving you the best of both worlds!
