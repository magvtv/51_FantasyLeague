# Supabase Database Setup Guide

## Overview

Your NFL Fantasy League application has two approaches to create tables in Supabase:

1. **SQLAlchemy Models Approach** (`setup_supabase.py`) - Uses your `models.py` definitions
2. **Direct SQL Approach** (`setup_supabase_sql.py`) - Uses your `setup_database.sql` file

Both approaches will create the same tables, but they use different methods.

## Connection Types

For your CLI application, **Direct Connection** is recommended because:
- You have persistent, long-lived connections
- You're running on a local machine/VM
- You need reliable, stable connections

## Setup Instructions

### 1. Configure Environment Variables

Create a `.env` file in your project root with your Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT_REF].supabase.co:5432/postgres
```

### 2. Get Your Supabase Credentials

1. Go to your Supabase dashboard
2. Navigate to Settings → Database
3. Copy the connection string (Direct Connection)
4. Replace `[YOUR_PASSWORD]` with your database password
5. Replace `[YOUR_PROJECT_REF]` with your project reference

### 3. Choose Your Setup Method

#### Option A: SQLAlchemy Models (Recommended)
```bash
cd nfl_fantasy_cli
python setup_supabase.py
```

#### Option B: Direct SQL Script
```bash
cd nfl_fantasy_cli
python setup_supabase_sql.py
```

### 4. Verify Tables in Supabase Dashboard

After running either script:
1. Go to your Supabase dashboard
2. Navigate to Table Editor
3. You should see all your tables:
   - `users`
   - `nfl_players`
   - `fantasy_teams`
   - `team_players`
   - `weekly_lineups`
   - `weekly_scores`
   - `transfers`

## Troubleshooting

### Connection Issues
- **IP Whitelist**: Add your IP to Supabase dashboard → Settings → Database → Connection pooling
- **Password**: Ensure your database password is correct
- **Project Status**: Verify your Supabase project is active

### Table Creation Issues
- **Permissions**: Ensure your database user has CREATE TABLE permissions
- **Schema**: Tables will be created in the `public` schema
- **Conflicts**: Scripts handle existing tables gracefully

## File Comparison

| File | Purpose | Method |
|------|---------|--------|
| `models.py` | Defines table structure using SQLAlchemy ORM | ORM Models |
| `setup_database.sql` | Raw SQL table creation script | Direct SQL |
| `database.py` | Database connection and configuration | Connection Layer |
| `setup_supabase.py` | Creates tables using SQLAlchemy models | ORM Approach |
| `setup_supabase_sql.py` | Runs SQL script directly | SQL Approach |

## Recommendation

Use **Option A (SQLAlchemy Models)** because:
- It's consistent with your application's ORM approach
- Easier to maintain and modify
- Better integration with your Flask-SQLAlchemy setup
- Automatic schema validation

The `setup_database.sql` file is useful as a reference and backup, but the SQLAlchemy approach is more maintainable for your application.
