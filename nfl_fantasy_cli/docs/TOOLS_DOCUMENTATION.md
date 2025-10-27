# 🛠️ Development Tools Documentation

This document provides comprehensive documentation for the development tools in the `tools/` directory of the NFL Fantasy League CLI.

## 📁 Directory Structure

```
tools/
├── analysis/                 # JSON structure analysis tools
│   ├── analyze_json_structure.py
│   ├── analyze_json_structure_fixed.py
│   └── README.md
├── integration/              # Data integration and parsing tools
│   ├── fantasy_league_integration.py
│   ├── nfl_fantasy_parsers.py
│   ├── process_real_data.py
│   ├── working_data_processor.py
│   └── README.md
├── demos/                    # Demonstration scripts
│   ├── real_data_cli_demo.py
│   └── README.md
└── README.md                 # Tools overview
```

## 🔍 Analysis Tools (`tools/analysis/`)

### Purpose
Tools for analyzing NFL API JSON responses and understanding data structures for fantasy league integration.

### Files

#### `analyze_json_structure.py`
- **Purpose**: Initial JSON structure analyzer
- **Status**: Legacy version
- **Usage**: Basic analysis of NFL API responses

#### `analyze_json_structure_fixed.py`
- **Purpose**: Enhanced JSON structure analyzer with error handling
- **Status**: Current version
- **Features**:
  - Comprehensive error handling
  - Detailed structure analysis
  - Fantasy-relevant data extraction
  - Safe data access patterns

### Usage Examples

```bash
# Run the fixed analyzer
python3 tools/analysis/analyze_json_structure_fixed.py
```

### Output
- Live scores structure analysis
- Player detail structure analysis
- Team roster structure analysis
- Team injuries structure analysis
- Player statistics structure analysis
- NFL calendar structure analysis

## 🔗 Integration Tools (`tools/integration/`)

### Purpose
Tools for integrating real NFL API data into the fantasy league system with structured parsing and processing.

### Files

#### `nfl_fantasy_parsers.py`
- **Purpose**: Structured JSON parsers for fantasy league
- **Status**: Main integration tool
- **Features**:
  - Clean data extraction from complex JSON
  - Fantasy-relevant filtering (QB, RB, WR, TE, K, DEF)
  - Consistent data format for database integration
  - Error handling for all data structure variations

#### `fantasy_league_integration.py`
- **Purpose**: Integration guide and examples
- **Status**: Documentation and examples
- **Features**:
  - Step-by-step integration examples
  - Code snippets for database integration
  - Fantasy point calculation examples
  - Real-time update examples

#### `working_data_processor.py`
- **Purpose**: Working data processor with error handling
- **Status**: Robust data processor
- **Features**:
  - Safe data access patterns
  - Error handling for missing data
  - Fantasy-relevant data extraction
  - Progress tracking

#### `process_real_data.py`
- **Purpose**: Legacy data processor
- **Status**: Deprecated
- **Note**: Use `working_data_processor.py` instead

### Usage Examples

```bash
# Test structured parsers
python3 tools/integration/nfl_fantasy_parsers.py

# Run integration examples
python3 tools/integration/fantasy_league_integration.py

# Test working data processor
python3 tools/integration/working_data_processor.py
```

### Key Features

#### **Live Scores Parsing**
```python
def parse_live_scores(self):
    """Parse live NFL game scores"""
    data = self.api_service.get_live_scores()
    if not data or 'live' not in data:
        return None
    
    games = []
    for game in data['live']:
        game_info = {
            'game_id': game.get('id'),
            'competition': game.get('competitionDisplayName'),
            'round': game.get('roundName'),
            'start_time': game.get('startTime'),
            'status': game.get('statusText'),
            'home_team': game.get('homeCompetitor', {}).get('name'),
            'away_team': game.get('awayCompetitor', {}).get('name'),
            'home_score': game.get('homeCompetitor', {}).get('score'),
            'away_score': game.get('awayCompetitor', {}).get('score'),
            'winner': game.get('winner')
        }
        games.append(game_info)
    return games
```

#### **Player Detail Parsing**
```python
def parse_player_detail(self, player_id):
    """Parse detailed player information"""
    data = self.api_service.get_player_detail(player_id)
    if not data:
        return None
    
    return {
        'player_id': data.get('id'),
        'name': data.get('displayName'),
        'first_name': data.get('firstName'),
        'last_name': data.get('lastName'),
        'jersey': data.get('jersey'),
        'height': data.get('displayHeight'),
        'weight': data.get('displayWeight'),
        'age': data.get('age'),
        'experience': data.get('experience', {}).get('years'),
        'status': data.get('status', {}).get('name'),
        'college': data.get('college', {}).get('name')
    }
```

## 🎮 Demo Tools (`tools/demos/`)

### Purpose
Demonstration scripts showing how to use the NFL API and parsers in practice.

### Files

#### `real_data_cli_demo.py`
- **Purpose**: CLI demonstration using real NFL API data
- **Status**: Active demonstration tool
- **Features**:
  - Live scores demonstration
  - Player details demonstration
  - Team roster demonstration
  - Team injuries demonstration
  - NFL calendar demonstration

### Usage Examples

```bash
# Run the CLI demo
python3 tools/demos/real_data_cli_demo.py
```

### Demo Features

#### **Live Scores Demo**
```python
def show_live_scores():
    """Show live NFL scores"""
    print("🏈 LIVE NFL SCORES")
    print("=" * 30)
    
    data = nfl_api.get_live_scores()
    if data and 'live' in data:
        for game in data['live'][:3]:  # Show first 3 games
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            print(f"{away.get('name', 'Unknown')} {away.get('score', 0)} @ {home.get('name', 'Unknown')} {home.get('score', 0)}")
            print(f"Status: {game.get('statusText', 'Unknown')}")
            print()
    else:
        print("No live games available")
```

## 🚀 Getting Started

### 1. **Environment Setup**
```bash
# Activate virtual environment
source venv/bin/activate

# Ensure API key is configured
echo $RAPIDAPI_KEY
```

### 2. **Test API Connectivity**
```bash
# Test basic API connectivity
python3 tools/integration/nfl_fantasy_parsers.py
```

### 3. **Run Analysis Tools**
```bash
# Analyze JSON structures
python3 tools/analysis/analyze_json_structure_fixed.py
```

### 4. **Run Demo**
```bash
# See real data in action
python3 tools/demos/real_data_cli_demo.py
```

## 🔧 Development Workflow

### **Adding New API Endpoints**

1. **Add to API Service** (`app/api_service.py`)
```python
def get_new_endpoint(self, param):
    """Get data from new endpoint"""
    return self._get_request("new-endpoint", {"param": param})
```

2. **Add Parser** (`tools/integration/nfl_fantasy_parsers.py`)
```python
def parse_new_endpoint(self, param):
    """Parse new endpoint data"""
    data = self.api_service.get_new_endpoint(param)
    if not data:
        return None
    
    return {
        'field1': data.get('field1'),
        'field2': data.get('field2')
    }
```

3. **Add CLI Command** (`app/commands/api.py`)
```python
@api_commands.command()
@click.option('--param', required=True, help='Parameter for new endpoint')
def new_endpoint(param):
    """Get data from new endpoint"""
    data = nfl_api.get_new_endpoint(param)
    if data:
        console.print(f"New endpoint data: {data}")
    else:
        console.print("Failed to fetch data", style="red")
```

4. **Test Integration**
```bash
# Test new endpoint
python3 cli.py api new-endpoint --param value

# Test parser
python3 tools/integration/nfl_fantasy_parsers.py
```

### **Debugging Data Issues**

1. **Use Analysis Tools**
```bash
python3 tools/analysis/analyze_json_structure_fixed.py
```

2. **Check API Responses**
```bash
python3 tools/integration/working_data_processor.py
```

3. **Test Individual Endpoints**
```bash
python3 cli.py api live-scores
python3 cli.py api player-detail --player-id 4360644
```

## 📊 Data Flow

```
NFL API → API Service → Parsers → Database → Fantasy League
    ↓         ↓          ↓         ↓           ↓
Raw JSON → Structured → Clean → Stored → Used in
Response   Data        Data    Data     Fantasy Logic
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check Python path configuration
   - Verify API service import paths

2. **API Errors**
   - Verify RAPIDAPI_KEY is set
   - Check API quota limits
   - Test individual endpoints

3. **Data Parsing Errors**
   - Use analysis tools to understand structure
   - Check for missing fields in responses
   - Verify data types and formats

### **Debug Commands**

```bash
# Test API connectivity
python3 -c "from app.api_service import nfl_api; print(nfl_api.get_live_scores())"

# Test parser
python3 -c "from tools.integration.nfl_fantasy_parsers import NFLFantasyParsers; p = NFLFantasyParsers(); print(p.parse_live_scores())"

# Check environment
python3 -c "import os; print('API Key:', bool(os.getenv('RAPIDAPI_KEY')))"
```

## 📚 Additional Resources

- [Integration Summary](../docs/INTEGRATION_SUMMARY.md)
- [Setup Guide](../docs/SETUP_GUIDE.md)
- [Data Management](../docs/DATA_MANAGEMENT.md)
- [Project Structure](../PROJECT_STRUCTURE.md)

---

**The development tools provide everything needed to integrate real NFL data into your fantasy league system!** 🏈✨
