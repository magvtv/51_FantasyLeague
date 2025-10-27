# Integration Tools

This directory contains tools for integrating real NFL API data into the fantasy league system.

## Files

- **`nfl_fantasy_parsers.py`** - Structured JSON parsers for fantasy league
- **`fantasy_league_integration.py`** - Integration guide and examples
- **`process_real_data.py`** - Real data processor (legacy)
- **`working_data_processor.py`** - Working data processor with error handling

## Usage

```bash
# Run the main parsers demo
python3 nfl_fantasy_parsers.py

# Run the integration guide
python3 fantasy_league_integration.py
```

## Purpose

These tools provide structured parsing of NFL API data specifically formatted for fantasy league use, including:

- Live score parsing
- Player detail extraction
- Team roster management
- Injury monitoring
- Statistics processing
- Calendar integration
