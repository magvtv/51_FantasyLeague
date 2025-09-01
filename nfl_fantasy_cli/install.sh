#!/bin/bash

# NFL Fantasy League CLI Installation Script

echo "🏈 NFL Fantasy League CLI Installation"
echo "======================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy env.example to .env and configure your settings:"
echo "   cp env.example .env"
echo "   nano .env"
echo ""
echo "2. Set up Supabase (Recommended):"
echo "   - Go to https://supabase.com"
echo "   - Create a new project"
echo "   - Get your project URL and anon key"
echo "   - Update SUPABASE_URL and SUPABASE_KEY in .env"
echo "   - Get your database connection string from Settings > Database"
echo "   - Update SUPABASE_DB_URL in .env"
echo ""
echo "3. Get RapidAPI key for NFL data:"
echo "   - Visit https://rapidapi.com/Creativesdev/api/nfl-api-data"
echo "   - Subscribe to get your API key"
echo "   - Update RAPIDAPI_KEY in .env"
echo ""
echo "4. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "5. Initialize database:"
echo "   python cli.py init"
echo ""
echo "6. Start using the CLI:"
echo "   python cli.py --help"
echo ""
echo "🎯 Happy fantasy football managing!"
