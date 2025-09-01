# NFL Fantasy League - Complete Setup Guide

## 🚀 Quick Start

This guide will help you set up the NFL Fantasy League CLI with PostgreSQL database integration.

## 📋 Prerequisites

### 1. System Requirements
- **Python 3.8+**
- **PostgreSQL 12+**
- **Git**
- **RapidAPI Account** (for NFL data)

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
# PostgreSQL Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nfl_fantasy

# NFL API Configuration (RapidAPI)
RAPIDAPI_KEY=your_rapidapi_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### Step 3: Database Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database using management script
cd scripts
./db_management.sh init
```

This will:
- Create the `nfl_fantasy` database
- Set up all tables with proper relationships
- Create indexes for performance
- Insert sample data for testing

### Step 4: Import NFL Data

```bash
# Import real NFL player data (optional)
python import_nfl_data.py
```

This script will:
- Fetch NFL team data from RapidAPI
- Import player information with calculated prices
- Generate sample weekly scores for testing

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
python cli.py status

# Initialize database (if not done via scripts)
python cli.py init
```

#### User Management
```bash
# Register new user
python cli.py user register --username john_doe --email john@example.com

# List all users
python cli.py user list

# View user profile
python cli.py user profile --username john_doe
```

#### Team Management
```bash
# Create fantasy team
python cli.py team create --user-id 1 --name "John's Warriors"

# Search for players
python cli.py team search --position QB --limit 10
python cli.py team search --team KC --max-price 10000000

# Draft a player
python cli.py team draft --team-id 1 --player-id 123

# View team details
python cli.py team show --team-id 1

# Transfer players
python cli.py team transfer --team-id 1 --player-out 123 --player-in 456 --week 2
```

#### Gameweek Operations
```bash
# Set up weekly lineup
python cli.py gameweek setup --team-id 1 --week 1

# View lineup
python cli.py gameweek lineup --team-id 1 --week 1

# Calculate weekly points
python cli.py gameweek calculate --team-id 1 --week 1

# View leaderboard
python cli.py gameweek leaderboard --week 1
```

## 🛠️ Database Management

### Backup Operations

```bash
cd scripts

# Create backup
./db_management.sh backup

# Restore from backup
./db_management.sh restore backups/nfl_fantasy_backup_20241201_143022.sql.gz

# View database statistics
./db_management.sh stats
```

### Data Export

```bash
# Export table to CSV
./db_management.sh export nfl_players csv

# Export to JSON
./db_management.sh export weekly_scores json
```

### Maintenance

```bash
# Clean old backups (older than 30 days)
./db_management.sh clean

# Custom cleanup (older than 7 days)
./db_management.sh clean 7
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
# Connect to database
psql nfl_fantasy

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

1. **Models**: Update `nfl_fantasy_cli/app/models.py`
2. **Logic**: Add business logic to `nfl_fantasy_cli/app/fantasy_logic.py`
3. **Commands**: Create CLI commands in `nfl_fantasy_cli/app/commands/`
4. **Database**: Update `scripts/setup_database.sql` for schema changes

### Testing Changes

```bash
# Reset database for testing
cd scripts
./db_management.sh init

# Import fresh test data
python import_nfl_data.py

# Test CLI commands
# Already in nfl_fantasy_cli directory
python cli.py user register --username test_user --email test@example.com
python cli.py team create --user-id 1 --name "Test Team"
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

1. **Complete CLI Testing**: Verify all features work
2. **Add Real NFL Data**: Configure RapidAPI integration
3. **Performance Tuning**: Optimize database queries
4. **Django Planning**: Design REST API structure
5. **Frontend Design**: Plan SvelteKit components

Happy fantasy football managing! 🏈
