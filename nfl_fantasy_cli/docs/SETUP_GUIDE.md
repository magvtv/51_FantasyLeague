# NFL Fantasy League - Complete Setup Guide

## 🚀 Quick Start

This guide will help you set up the NFL Fantasy League CLI with PostgreSQL database integration and real NFL API data.

## 📋 Prerequisites

### 1. System Requirements
- **Python 3.8+**
- **PostgreSQL 12+** (or SQLite for development)
- **Git**
- **RapidAPI Account** (for NFL data)
- **Virtual Environment** (venv)

### 2. Install PostgreSQL

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS:
```bash
brew install postgresql
brew services start postgresql
```

#### Windows:
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 3. Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database user (optional)
CREATE USER nfl_fantasy_user WITH PASSWORD 'secure_password';
ALTER USER nfl_fantasy_user CREATEDB;

# Exit psql
\q
```

## 🏗️ Installation

### Step 1: Clone and Setup Environment

```bash
# Navigate to project directory
cd 51_FantasyLeague/nfl_fantasy_cli

# Run automated installation
./install.sh
```

This script will:
- Create Python virtual environment
- Install all dependencies
- Set up directory structure

### Step 2: Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env
```

Configure your `.env` file:
```env
# Database Configuration (choose one)
# PostgreSQL
SUPABASE_DB_URL=postgresql://user:password@host:port/database
# OR SQLite (for development)
DATABASE_URL=sqlite:///instance/nfl_fantasy.db

# NFL API Configuration (RapidAPI)
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=nfl-api-data.p.rapidapi.com

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### Step 3: Database Setup

```bash
# Activate virtual environment
source venv/bin/activate

# For SQLite (development)
bash setup_sqlite.sh

# For Supabase PostgreSQL (production)
bash setup_modular_teams.sh
```

This will:
- Create the database
- Set up all tables with proper relationships
- Create indexes for performance
- Insert sample data for testing

### Step 4: Test Real NFL API Integration

```bash
# Test API connectivity
python3 tools/integration/nfl_fantasy_parsers.py

# Run CLI demo with real data
python3 tools/demos/real_data_cli_demo.py

# Analyze JSON structures
python3 tools/analysis/analyze_json_structure_fixed.py
```

This will:
- Test all NFL API endpoints
- Verify real data integration
- Show structured data parsing
- Demonstrate CLI functionality

## 🎮 Using the CLI

### Activate Environment
```bash
# From the nfl_fantasy_cli directory
source venv/bin/activate
```

### Basic Commands

#### System Management
```bash
# Check system status
python3 cli.py status

# Initialize database (if not done via scripts)
python3 cli.py init
```

#### API Data Management
```bash
# Live NFL data
python3 cli.py api live-scores
python3 cli.py api calendar

# Player data
python3 cli.py api player-detail --player-id 4360644
python3 cli.py api player-stats --player-id 15035 --year 2023

# Team data
python3 cli.py api team-roster --team-id 22
python3 cli.py api team-injuries --team-id 22
python3 cli.py api team-statistics --team-id 22 --year 2023

# Analysis
python3 cli.py api analyze-player --player-id 4360644
python3 cli.py api analyze-team --team-id 22
```

#### User Management
```bash
# Register new user
python3 cli.py user register --username john_doe --email john@example.com

# List all users
python3 cli.py user list

# View user profile
python3 cli.py user profile --username john_doe
```

#### Team Management
```bash
# Create fantasy team
python3 cli.py team create --user-id 1 --name "John's Warriors"

# Search for players
python3 cli.py team search --position QB --limit 10
python3 cli.py team search --team KC --max-price 10000000

# Draft a player
python3 cli.py team draft --team-id 1 --player-id 123

# View team details
python3 cli.py team show --team-id 1

# Transfer players
python3 cli.py team transfer --team-id 1 --player-out 123 --player-in 456 --week 2
```

#### Gameweek Operations
```bash
# Set up weekly lineup
python3 cli.py gameweek setup --team-id 1 --week 1

# View lineup
python3 cli.py gameweek lineup --team-id 1 --week 1

# Calculate weekly points
python3 cli.py gameweek calculate --team-id 1 --week 1

# View leaderboard
python3 cli.py gameweek leaderboard --week 1
```

## 🛠️ Development Tools

### Analysis Tools (`tools/analysis/`)
```bash
# Analyze NFL API JSON structures
python3 tools/analysis/analyze_json_structure_fixed.py

# Understand data formats for integration
python3 tools/analysis/analyze_json_structure.py
```

### Integration Tools (`tools/integration/`)
```bash
# Test structured data parsers
python3 tools/integration/nfl_fantasy_parsers.py

# Integration examples and guides
python3 tools/integration/fantasy_league_integration.py

# Working data processor
python3 tools/integration/working_data_processor.py
```

### Demo Tools (`tools/demos/`)
```bash
# CLI demonstration with real data
python3 tools/demos/real_data_cli_demo.py
```

## 🛠️ Database Management

### SQLite (Development)
```bash
# Initialize SQLite database
bash setup_sqlite.sh

# View database
sqlite3 instance/nfl_fantasy.db
```

### Supabase PostgreSQL (Production)
```bash
# Initialize Supabase database
bash setup_modular_teams.sh

# Connect to database
psql $SUPABASE_DB_URL
```

## 📊 Database Schema Overview

### Core Tables

1. **users** - User accounts
2. **nfl_players** - NFL player data with fantasy pricing
3. **fantasy_teams** - User-owned fantasy teams
4. **team_players** - Team rosters (many-to-many)
5. **weekly_lineups** - Starting lineups per gameweek
6. **weekly_scores** - Player performance data
7. **transfers** - Transfer history with costs

### Useful Views

- **team_summary** - Complete team overview with stats
- **weekly_leaderboard** - Ranked teams by week

### Direct SQL Access

```bash
# Connect to database (SQLite)
sqlite3 instance/nfl_fantasy.db

# Connect to database (PostgreSQL)
psql $SUPABASE_DB_URL

# View team summary
SELECT * FROM team_summary;

# View weekly leaderboard for week 1
SELECT * FROM weekly_leaderboard WHERE week = 1;

# Check player prices by position
SELECT position, AVG(price) as avg_price, COUNT(*) as player_count 
FROM nfl_players 
GROUP BY position 
ORDER BY avg_price DESC;
```

## 🔧 Development Workflow

### Adding New Features

1. **Models**: Update `app/models.py`
2. **Logic**: Add business logic to `app/fantasy_logic.py`
3. **Commands**: Create CLI commands in `app/commands/`
4. **API Service**: Add new endpoints to `app/api_service.py`
5. **Database**: Update `scripts/setup_database.sql` for schema changes
6. **Tools**: Add analysis/integration tools to `tools/` directory

### Testing Changes

```bash
# Test API integration
python3 tools/integration/nfl_fantasy_parsers.py

# Test CLI commands
python3 cli.py user register --username test_user --email test@example.com
python3 cli.py team create --user-id 1 --name "Test Team"

# Test real data
python3 tools/demos/real_data_cli_demo.py
```

## 🌐 Transition to Web Application

### Django Migration Plan

1. **Keep PostgreSQL Database**: Same schema, different ORM
2. **Convert Models**: Translate SQLAlchemy models to Django models
3. **API Layer**: Create Django REST Framework endpoints
4. **Frontend**: Build SvelteKit interface

### Preparing for Django

```bash
# Export current data
cd scripts
./db_management.sh backup

# The PostgreSQL schema is already Django-compatible
# You can use the same database with Django
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check PostgreSQL status
systemctl status postgresql

# Test connection
pg_isready -h localhost -p 5432
```

#### 2. Permission Errors
```bash
# Fix PostgreSQL permissions
sudo -u postgres psql -c "ALTER USER your_user CREATEDB;"
```

#### 3. Import Errors
```bash
# Activate virtual environment
source venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 4. API Errors
- Verify RAPIDAPI_KEY in `.env`
- Check API quota limits
- Test API connectivity

### Log Files

- **CLI Logs**: Check terminal output
- **PostgreSQL Logs**: `/var/log/postgresql/`
- **API Responses**: Enable debug mode in `.env`

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Click CLI Documentation](https://click.palletsprojects.com/)
- [Rich Terminal Documentation](https://rich.readthedocs.io/)

## 🎯 Next Steps

1. **✅ Real NFL Data Integration**: Complete with 11 API endpoints
2. **✅ Structured Data Parsing**: JSON parsers for fantasy league
3. **✅ Development Tools**: Analysis, integration, and demo tools
4. **Performance Tuning**: Optimize database queries
5. **Django Planning**: Design REST API structure
6. **Frontend Design**: Plan SvelteKit components

## 📚 Additional Resources

- [Project Structure Guide](PROJECT_STRUCTURE.md)
- [Integration Summary](INTEGRATION_SUMMARY.md)
- [Tools Documentation](tools/README.md)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Click CLI Documentation](https://click.palletsprojects.com/)
- [Rich Terminal Documentation](https://rich.readthedocs.io/)

Happy fantasy football managing! 🏈✨
