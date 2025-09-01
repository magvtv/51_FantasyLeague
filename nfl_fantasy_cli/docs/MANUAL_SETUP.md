# Supabase Database Setup - Simplified Guide

## Current Status

✅ **Clean Setup**: We've consolidated all database files into a single, clean configuration
✅ **SQL Script Ready**: Your `setup_database.sql` contains all necessary table definitions
✅ **Simple Setup**: One script to rule them all: `setup_database.py`

## What We've Cleaned Up

- ❌ Removed redundant `database.py` (replaced with `database_supabase.py` → `database.py`)
- ❌ Removed `setup_supabase.py` (replaced with `setup_database.py`)
- ❌ Removed `setup_supabase_sql.py` (replaced with `show_sql.py`)
- ❌ Removed `db_management.sh` (not needed for Supabase)

## Current File Structure

```
nfl_fantasy_cli/
├── app/
│   ├── database.py          # Main database configuration (Supabase)
│   └── models.py            # SQLAlchemy table definitions
├── scripts/
│   └── setup_database.sql   # SQL script for manual execution
├── setup_database.py        # Simple setup script
└── show_sql.py             # Display SQL content for manual execution
```

## Setup Options

### Option 1: Automatic Setup (Recommended)
```bash
cd nfl_fantasy_cli
python setup_database.py
```

### Option 2: Manual SQL Execution
```bash
cd nfl_fantasy_cli
python show_sql.py
```
Then copy the output and paste it into Supabase SQL Editor.

## Quick Setup Steps

1. **Ensure your `.env` file has:**
   ```
   SUPABASE_DB_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT_REF].supabase.co:5432/postgres
   ```

2. **Run the setup:**
   ```bash
   python setup_database.py
   ```

3. **If automatic fails, use manual:**
   ```bash
   python show_sql.py
   ```
   Then execute the SQL in Supabase dashboard.

## What You'll Get

After successful setup, you'll have these tables in Supabase:
- `users` - User accounts
- `nfl_players` - NFL player data  
- `fantasy_teams` - User teams
- `team_players` - Team rosters
- `weekly_lineups` - Gameweek lineups
- `weekly_scores` - Player performance
- `transfers` - Transfer history

## Why This is Better

1. **No Redundancy**: Single database configuration file
2. **Clear Purpose**: Each file has one job
3. **Easy Maintenance**: Simple to understand and modify
4. **Supabase Focused**: Built specifically for your Supabase setup
5. **Fallback Options**: Automatic setup + manual SQL execution
