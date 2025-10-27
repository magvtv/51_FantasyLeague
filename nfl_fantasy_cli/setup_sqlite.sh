#!/bin/bash
# Simplified setup script for NFL Fantasy League CLI with SQLite

set -e

echo "🚀 NFL Fantasy League CLI - SQLite Setup"
echo "======================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Local SQLite Configuration (for development)
SQLITE_DB_PATH=./nfl_fantasy_local.db

# NFL API Configuration (RapidAPI)
RAPIDAPI_HOST=nfl-api-data.p.rapidapi.com
RAPIDAPI_KEY=your_rapidapi_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Initialize database with SQLite
echo "🗄️  Initializing SQLite database..."
python3 -c "
import sys
sys.path.append('app')
from database import init_db, test_connection

if test_connection():
    init_db()
    print('✅ SQLite database initialized successfully')
else:
    print('❌ Database initialization failed')
    exit(1)
"

# Create NFL teams data
echo "🏈 Creating NFL teams data..."
python3 -c "
import sys
sys.path.append('app')
from database import get_app, get_db
from models import NFLTeam

app = get_app()
db = get_db()

with app.app_context():
    # Check if teams already exist
    if NFLTeam.query.count() == 0:
        teams = [
            ('ARI', 'Arizona Cardinals', 'Arizona', 'Cardinals'),
            ('ATL', 'Atlanta Falcons', 'Atlanta', 'Falcons'),
            ('BAL', 'Baltimore Ravens', 'Baltimore', 'Ravens'),
            ('BUF', 'Buffalo Bills', 'Buffalo', 'Bills'),
            ('CAR', 'Carolina Panthers', 'Carolina', 'Panthers'),
            ('CHI', 'Chicago Bears', 'Chicago', 'Bears'),
            ('CIN', 'Cincinnati Bengals', 'Cincinnati', 'Bengals'),
            ('CLE', 'Cleveland Browns', 'Cleveland', 'Browns'),
            ('DAL', 'Dallas Cowboys', 'Dallas', 'Cowboys'),
            ('DEN', 'Denver Broncos', 'Denver', 'Broncos'),
            ('DET', 'Detroit Lions', 'Detroit', 'Lions'),
            ('GB', 'Green Bay Packers', 'Green Bay', 'Packers'),
            ('HOU', 'Houston Texans', 'Houston', 'Texans'),
            ('IND', 'Indianapolis Colts', 'Indianapolis', 'Colts'),
            ('JAX', 'Jacksonville Jaguars', 'Jacksonville', 'Jaguars'),
            ('KC', 'Kansas City Chiefs', 'Kansas City', 'Chiefs'),
            ('LV', 'Las Vegas Raiders', 'Las Vegas', 'Raiders'),
            ('LAC', 'Los Angeles Chargers', 'Los Angeles', 'Chargers'),
            ('LAR', 'Los Angeles Rams', 'Los Angeles', 'Rams'),
            ('MIA', 'Miami Dolphins', 'Miami', 'Dolphins'),
            ('MIN', 'Minnesota Vikings', 'Minnesota', 'Vikings'),
            ('NE', 'New England Patriots', 'New England', 'Patriots'),
            ('NO', 'New Orleans Saints', 'New Orleans', 'Saints'),
            ('NYG', 'New York Giants', 'New York', 'Giants'),
            ('NYJ', 'New York Jets', 'New York', 'Jets'),
            ('PHI', 'Philadelphia Eagles', 'Philadelphia', 'Eagles'),
            ('PIT', 'Pittsburgh Steelers', 'Pittsburgh', 'Steelers'),
            ('SF', 'San Francisco 49ers', 'San Francisco', '49ers'),
            ('SEA', 'Seattle Seahawks', 'Seattle', 'Seahawks'),
            ('TB', 'Tampa Bay Buccaneers', 'Tampa Bay', 'Buccaneers'),
            ('TEN', 'Tennessee Titans', 'Tennessee', 'Titans'),
            ('WAS', 'Washington Commanders', 'Washington', 'Commanders')
        ]
        
        for team_code, team_name, city, nickname in teams:
            team = NFLTeam(
                team_code=team_code,
                team_name=team_name,
                city=city,
                nickname=nickname
            )
            db.session.add(team)
        
        db.session.commit()
        print(f'✅ Created {len(teams)} NFL teams')
    else:
        print('✅ NFL teams already exist')
"

# Prefill Tampa Bay data
echo "🏈 Prefilling Tampa Bay Buccaneers data for weeks 1-8..."
python3 scripts/prefill_tampa_bay_data.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 What was set up:"
echo "✅ SQLite database (local development)"
echo "✅ NFL teams data"
echo "✅ Tampa Bay historical data (weeks 1-8)"
echo "✅ Modular team system"
echo ""
echo "🏈 Available commands:"
echo "   python3 cli.py status"
echo "   python3 cli.py gameweek setup-offense --team-id 1 --week 9"
echo "   python3 cli.py gameweek setup-defense --team-id 1 --week 9 --nfl-team TB"
echo "   python3 cli.py gameweek setup-special --team-id 1 --week 9 --nfl-team TB"
echo "   python3 cli.py gameweek view-modular --team-id 1 --week 9"
echo "   python3 cli.py gameweek cumulative --team-id 1 --week 9"
echo ""
echo "📊 Database: SQLite (nfl_fantasy.db)"
echo "🔒 Security: Row-Level Security not applicable for SQLite"
echo "📈 Historical data: Weeks 1-8 use Tampa Bay Buccaneers"
echo "🎯 Starting week: You can now customize lineups from week 9"
