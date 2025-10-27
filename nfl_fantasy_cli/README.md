# 🏈 NFL Fantasy League CLI

A comprehensive command-line interface for managing NFL fantasy leagues with real-time data integration.

## ✨ Features

- **Real NFL API Integration** - Live scores, player data, injuries, and statistics
- **Modular Team Management** - Separate offense, defense, and special teams
- **Database Support** - SQLite and Supabase PostgreSQL
- **CLI Interface** - Easy-to-use command-line tools
- **Data Sync** - Automatic synchronization with NFL data
- **Fantasy Logic** - Complete fantasy league management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip3
- Database (SQLite or Supabase)

### Installation

1. **Clone and setup**
```bash
git clone <repository>
cd nfl_fantasy_cli
bash install.sh
```

2. **Configure environment**
```bash
cp env.example .env
# Edit .env with your API keys and database credentials
```

3. **Setup database**
```bash
# For SQLite
bash setup_sqlite.sh

# For Supabase
bash setup_modular_teams.sh
```

4. **Run the CLI**
```bash
python3 cli.py --help
```

## 📁 Project Structure

```
nfl_fantasy_cli/
├── app/                    # Main application code
├── tools/                  # Development tools
│   ├── analysis/          # JSON structure analysis
│   ├── integration/       # Data integration tools
│   └── demos/             # Demonstration scripts
├── scripts/               # Database and setup scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
└── data/                  # Static data files
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed organization.

## 🎯 Usage

### **Main Commands**

```bash
# API data management
python3 cli.py api live-scores
python3 cli.py api player-detail --player-id 4360644
python3 cli.py api team-roster --team-id 22

# Team management
python3 cli.py team create --name "My Team"
python3 cli.py team list

# Gameweek management
python3 cli.py gameweek setup-offense --team-id 1 --week 9
python3 cli.py gameweek view-modular --team-id 1 --week 9

# Data synchronization
python3 cli.py data sync-players
python3 cli.py data sync-scores
```

### **Development Tools**

```bash
# Analyze NFL API JSON structure
python3 tools/analysis/analyze_json_structure_fixed.py

# Test data parsers
python3 tools/integration/nfl_fantasy_parsers.py

# Run CLI demo
python3 tools/demos/real_data_cli_demo.py
```

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file with:

```bash
# Database
SUPABASE_DB_URL=your_supabase_connection_string
DATABASE_URL=sqlite:///instance/nfl_fantasy.db

# NFL API
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=nfl-api-data.p.rapidapi.com
```

### **Database Setup**

The system supports both SQLite (development) and Supabase PostgreSQL (production):

- **SQLite**: `bash setup_sqlite.sh`
- **Supabase**: `bash setup_modular_teams.sh`

## 📊 Real NFL Data Integration

The system integrates with real NFL API endpoints:

- **Live Scores** - Real-time game scores and status
- **Player Details** - Complete player information
- **Team Rosters** - Current team rosters and depth charts
- **Injury Reports** - Player injury status and updates
- **Statistics** - Player performance data by season/week
- **Calendar** - NFL schedule and event dates

## 🏈 Fantasy League Features

### **Modular Team System**
- **Offense** - QB, RB1, RB2, WR1, WR2, TE
- **Defense** - Individual players or entire team
- **Special Teams** - Kicker, Punter, or entire team

### **Gameweek Management**
- Set lineups for each week
- Track cumulative points
- Manage transfers and budget
- View league standings

### **Real-time Updates**
- Live score tracking
- Injury monitoring
- Player availability updates
- League standings updates

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test categories
python3 tests/test_api_endpoints.py
python3 tests/test_real_api.py
```

## 📚 Documentation

- [Setup Guide](docs/SETUP_GUIDE.md)
- [Data Management](docs/DATA_MANAGEMENT.md)
- [API Integration](docs/INTEGRATION_SUMMARY.md)
- [Project Structure](PROJECT_STRUCTURE.md)

## 🛠️ Development

### **Adding New Features**

1. **API Endpoints** - Add to `app/api_service.py`
2. **CLI Commands** - Add to `app/commands/`
3. **Data Models** - Add to `app/models.py`
4. **Business Logic** - Add to `app/fantasy_logic.py`

### **Testing New Features**

1. **Unit Tests** - Add to `tests/`
2. **Integration Tests** - Use tools in `tools/integration/`
3. **Analysis Tools** - Use tools in `tools/analysis/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the [documentation](docs/)
2. Review [setup guides](docs/SETUP_GUIDE.md)
3. Open an issue on GitHub

---

**Built with real NFL data for fantasy football enthusiasts!** 🏈✨
