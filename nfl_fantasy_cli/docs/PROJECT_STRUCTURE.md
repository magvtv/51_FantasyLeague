# NFL Fantasy League CLI - Project Structure

## 📁 Directory Organization

```
nfl_fantasy_cli/
├── app/                          # Main application code
│   ├── commands/                 # CLI command modules
│   │   ├── api.py               # API-related commands
│   │   ├── data.py              # Data management commands
│   │   ├── gameweek.py          # Gameweek management
│   │   ├── team.py              # Team management
│   │   └── user.py              # User management
│   ├── instance/                 # Database instance
│   ├── api_service.py           # NFL API service
│   ├── database.py              # Database configuration
│   ├── fantasy_logic.py         # Fantasy league logic
│   └── models.py                # Database models
├── data/                         # Static data files
│   ├── players.db               # Player database
│   └── teams.json               # Team data
├── docs/                         # Documentation
│   ├── CLEANUP_SUMMARY.md       # Cleanup documentation
│   ├── DATA_MANAGEMENT.md       # Data management guide
│   ├── DATA_SYNC_GUIDE.md       # Data sync guide
│   ├── INTEGRATION_SUMMARY.md   # API integration summary
│   ├── MANUAL_SETUP.md          # Manual setup guide
│   ├── SETUP_GUIDE.md           # Setup guide
│   ├── SETUP_SUMMARY.md         # Setup summary
│   └── SUPABASE_SETUP.md       # Supabase setup guide
├── scripts/                      # Database and setup scripts
│   ├── import_nfl_data.py       # NFL data import
│   ├── migrate_to_modular_teams.sql  # Database migration
│   ├── prefill_tampa_bay_data.py     # Sample data
│   ├── setup_complete_database.sql  # Complete DB setup
│   └── setup_database.sql       # Basic DB setup
├── tests/                        # Test files
│   ├── test_api_endpoints.py    # API endpoint tests
│   ├── test_detailed_api.py     # Detailed API tests
│   ├── test_enhanced_api.py     # Enhanced API tests
│   ├── test_final_api.py        # Final API tests
│   ├── test_real_api.py         # Real API tests
│   └── test_simple_api.py       # Simple API tests
├── tools/                        # Development tools
│   ├── analysis/                 # JSON structure analysis
│   │   ├── analyze_json_structure.py      # Initial analyzer
│   │   ├── analyze_json_structure_fixed.py # Fixed analyzer
│   │   └── README.md            # Analysis tools docs
│   ├── integration/              # Data integration tools
│   │   ├── fantasy_league_integration.py  # Integration guide
│   │   ├── nfl_fantasy_parsers.py        # JSON parsers
│   │   ├── process_real_data.py           # Data processor
│   │   ├── working_data_processor.py     # Working processor
│   │   └── README.md            # Integration tools docs
│   ├── demos/                    # Demonstration scripts
│   │   ├── real_data_cli_demo.py # CLI demo
│   │   └── README.md            # Demo tools docs
│   └── README.md                 # Tools overview
├── venv/                         # Virtual environment
├── cli.py                        # Main CLI entry point
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── env.example                   # Environment variables template
└── README.md                     # Main project documentation
```

## 🎯 **Key Directories**

### **`app/`** - Core Application
- Contains the main fantasy league application code
- CLI commands, database models, API service, and business logic

### **`tools/`** - Development Tools
- **`analysis/`** - JSON structure analysis tools
- **`integration/`** - Data integration and parsing tools
- **`demos/`** - Demonstration scripts and examples

### **`scripts/`** - Database Scripts
- SQL migration scripts
- Data import/export scripts
- Setup and configuration scripts

### **`tests/`** - Test Suite
- API endpoint tests
- Data processing tests
- Integration tests

### **`docs/`** - Documentation
- Setup guides
- API integration documentation
- Data management guides

## 🚀 **Usage**

### **Main Application**
```bash
# Run the CLI
python3 cli.py

# Available commands
python3 cli.py api --help
python3 cli.py team --help
python3 cli.py gameweek --help
```

### **Development Tools**
```bash
# JSON analysis
python3 tools/analysis/analyze_json_structure_fixed.py

# Data integration
python3 tools/integration/nfl_fantasy_parsers.py

# CLI demo
python3 tools/demos/real_data_cli_demo.py
```

### **Database Setup**
```bash
# Run setup scripts
bash setup_sqlite.sh
bash setup_modular_teams.sh

# Or run SQL directly
psql -d your_database -f scripts/setup_complete_database.sql
```

## 📋 **Best Practices Followed**

✅ **Lowercase naming** - All directories and files use lowercase
✅ **Clear separation** - Tools, tests, docs, and app code are separated
✅ **Logical grouping** - Related files are grouped together
✅ **Documentation** - Each directory has README files
✅ **Consistent structure** - Follows Python project conventions
✅ **Easy navigation** - Clear hierarchy and naming
