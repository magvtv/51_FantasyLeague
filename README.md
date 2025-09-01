## NFL Fantasy League CLI

A comprehensive command-line interface for managing NFL fantasy football teams with Supabase backend and real-time NFL data integration.

### 🏈 Features

- **Team Management**: Create and manage fantasy teams with $100M budget
- **Player Drafting**: Search and draft NFL players by position, team, and price
- **Weekly Lineups**: Set starting lineups for each gameweek
- **Scoring System**: PPR (Point Per Reception) fantasy scoring
- **Transfers**: Player transfers with free transfer limits and point penalties
- **Leaderboards**: Weekly rankings and team comparisons
- **Real-time Data**: Integration with NFL API for live stats and injury reports
- **API Exploration**: Comprehensive NFL API data access and exploration

### 🚀 Quick Start

#### Prerequisites
- Python 3.8+
- Supabase account (recommended) or PostgreSQL database
- RapidAPI account (for NFL data)

#### Installation

1. **Clone and Setup**
   ```bash
   cd 51_FantasyLeague/nfl_fantasy_cli
   ./install.sh
   ```

2. **Configure Environment**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit configuration
   nano .env
   ```

3. **Set up Supabase (Recommended)**
   - Go to https://supabase.com
   - Create a new project
   - Get your project URL and anon key
   - Update SUPABASE_URL and SUPABASE_KEY in .env
   - Get your database connection string from Settings > Database
   - Update SUPABASE_DB_URL in .env

4. **Get RapidAPI key for NFL data**
   - Visit https://rapidapi.com/Creativesdev/api/nfl-api-data
   - Subscribe to get your API key
   - Update RAPIDAPI_KEY in .env

5. **Initialize Database**
   ```bash
   source venv/bin/activate
   python cli.py init
   ```

#### Usage Examples

```bash
# User Management
python cli.py user register --username john_doe --email john@example.com
python cli.py user list
python cli.py user profile --username john_doe

# Team Management  
python cli.py team create --user-id 1 --name "John's Warriors"
python cli.py team show --team-id 1
python cli.py team search --position QB --limit 10
python cli.py team draft --team-id 1 --player-id 123

# Gameweek Operations
python cli.py gameweek setup --team-id 1 --week 1
python cli.py gameweek lineup --team-id 1 --week 1
python cli.py gameweek calculate --team-id 1 --week 1
python cli.py gameweek leaderboard --week 1

# NFL API Data Exploration
python cli.py api endpoints
python cli.py api teams --limit 10
python cli.py api players --team-id KC --limit 20
python cli.py api live-scores
python cli.py api news --limit 5
python cli.py api injuries
python cli.py api rankings --position QB

# System Status
python cli.py status
```

### 🏗️ Architecture

#### Database Schema (Supabase/PostgreSQL)
- **Users**: User accounts and authentication
- **NFLPlayer**: NFL player data with positions, teams, prices
- **FantasyTeam**: User teams with budgets and scoring
- **TeamPlayer**: Player ownership records
- **WeeklyLineup**: Starting lineups per gameweek
- **WeeklyScore**: Individual player performance data
- **Transfer**: Transfer history with costs and penalties

#### Scoring System (PPR)
- **Passing**: 1 pt/25 yards, 4 pts/TD, -2 pts/INT
- **Rushing**: 1 pt/10 yards, 6 pts/TD
- **Receiving**: 1 pt/10 yards, 6 pts/TD, 1 pt/reception
- **Kicking**: 3 pts/FG, 1 pt/XP
- **Defense**: 6 pts/TD, 2 pts/INT, points allowed scaling

#### Position Requirements
- 1 QB, 2 RB, 2 WR, 1 TE, 1 K, 1 DEF
- 15 player roster maximum
- $100M salary cap

### 🏈 NFL API Integration

The application integrates with the NFL API Data service from RapidAPI, providing access to:

#### Available Endpoints
- **Season & Calendar**: Current season, schedules, weekly/daily schedules
- **Teams**: Team listings, statistics, standings, depth charts
- **Players**: Player data, statistics, injuries, team rosters
- **Games & Scores**: Live scores, game details, play-by-play, odds
- **Statistics**: Passing, rushing, receiving, defensive, kicking stats
- **News & Media**: NFL news, team news, player news
- **Predictions**: Game predictions, player projections
- **Fantasy**: Fantasy points, rankings by position

#### API Commands
```bash
# Explore available endpoints
python cli.py api endpoints

# Get season information
python cli.py api season-info --season 2024

# View teams
python cli.py api teams --limit 10

# Get players for a team
python cli.py api players --team-id KC --limit 20

# Check live scores
python cli.py api live-scores

# Get injury reports
python cli.py api injuries

# View fantasy rankings
python cli.py api rankings --position QB --week 1

# Get NFL news
python cli.py api news --limit 5

# Cache management
python cli.py api cache-info
python cli.py api clear-cache
```

### 🔧 Development Roadmap

#### Phase 1: CLI Foundation ✅
- User registration and team creation
- Basic player drafting and roster management
- Supabase/PostgreSQL integration with SQLAlchemy
- CLI interface with Rich formatting

#### Phase 2: Game Logic (In Progress)
- Complete scoring algorithm implementation
- Weekly lineup management
- Transfer system with constraints
- Injury tracking and warnings

#### Phase 3: Data Integration ✅
- NFL API data synchronization
- Comprehensive API endpoint coverage
- Automated weekly score updates
- Player price adjustments
- Injury report integration

#### Phase 4: Web Application Transition
- Django backend development
- SvelteKit frontend
- API endpoint creation
- Database migration from Flask to Django

### 🛠️ Technical Stack

**Current (CLI)**:
- **Backend**: Flask + SQLAlchemy
- **Database**: Supabase (PostgreSQL)
- **CLI**: Click + Rich
- **API**: NFL Data via RapidAPI
- **Caching**: TTLCache

**Future (Web App)**:
- **Backend**: Django + Django REST Framework
- **Frontend**: SvelteKit + TypeScript
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Docker + cloud hosting

### 📚 API Integration

Uses NFL API Data from RapidAPI for:
- Team rosters and player information
- Weekly game statistics
- Injury reports and player status
- Live scores and game schedules
- Fantasy rankings and projections
- News and media content

### 🧪 Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Database reset for testing
python cli.py init --reset
```

### 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

### 📝 License

MIT License - see LICENSE file for details