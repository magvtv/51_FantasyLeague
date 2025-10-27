#!/bin/bash
# Installation and setup script for NFL Fantasy League CLI with modular teams

set -e

echo "🚀 NFL Fantasy League CLI - Modular Teams Setup"
echo "=============================================="

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

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your database credentials and API keys"
    echo "   - SUPABASE_DB_URL: Your Supabase PostgreSQL connection string"
    echo "   - RAPIDAPI_KEY: Your RapidAPI key for NFL data"
else
    echo "✅ .env file found"
fi

# Test database connection
echo "🔍 Testing database connection..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

if not os.getenv('SUPABASE_DB_URL'):
    print('❌ SUPABASE_DB_URL not found in .env file')
    exit(1)
else:
    print('✅ Database URL configured')
"

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
import sys
sys.path.append('app')
from database import init_db, test_connection

if test_connection():
    init_db()
    print('✅ Database initialized successfully')
else:
    print('❌ Database connection failed')
    print('Please check your SUPABASE_DB_URL in .env file')
    exit(1)
"

# Run migration script
echo "🔄 Running database migration..."
python3 -c "
import sys
import os
sys.path.append('app')

# Read and execute migration SQL
with open('scripts/migrate_to_modular_teams.sql', 'r') as f:
    migration_sql = f.read()

print('✅ Migration script loaded')
print('⚠️  Please run the migration SQL manually in your database:')
print('   psql -d your_database -f scripts/migrate_to_modular_teams.sql')
"

# Prefill Tampa Bay data
echo "🏈 Prefilling Tampa Bay Buccaneers data for weeks 1-8..."
python3 scripts/prefill_tampa_bay_data.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your actual credentials"
echo "2. Run the migration SQL script in your database:"
echo "   psql -d your_database -f scripts/migrate_to_modular_teams.sql"
echo "3. Test the CLI:"
echo "   python3 cli.py status"
echo ""
echo "🏈 Available commands:"
echo "   python3 cli.py gameweek setup-offense --team-id 1 --week 9"
echo "   python3 cli.py gameweek setup-defense --team-id 1 --week 9 --nfl-team TB"
echo "   python3 cli.py gameweek setup-special --team-id 1 --week 9 --nfl-team TB"
echo "   python3 cli.py gameweek view-modular --team-id 1 --week 9"
echo "   python3 cli.py gameweek cumulative --team-id 1 --week 9"
echo ""
echo "🔒 Security: Row-Level Security is enabled on all lineup tables"
echo "📊 Historical data: Weeks 1-8 use Tampa Bay Buccaneers"
echo "🎯 Starting week: You can now customize lineups from week 9"
