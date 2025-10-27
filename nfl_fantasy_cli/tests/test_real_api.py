#!/usr/bin/env python3
"""
Real API Test Script - Test actual NFL API endpoints
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from dotenv import load_dotenv
load_dotenv()

from api_service import nfl_api

def test_real_api():
    """Test real API endpoints"""
    print("🏈 Testing Real NFL API Endpoints")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print(f"🌐 Base URL: {nfl_api.base_url}")
    print()
    
    # Test 1: Live Scores
    print("1. Testing Live Scores...")
    try:
        live_scores = nfl_api.get_live_scores()
        if live_scores:
            print(f"✅ Live scores retrieved: {len(str(live_scores))} characters")
            print(f"📊 Sample data: {str(live_scores)[:200]}...")
        else:
            print("❌ No live scores data")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 2: Player Detail
    print("2. Testing Player Detail...")
    try:
        player_id = "4360644"  # From your example
        player_detail = nfl_api.get_player_detail(player_id)
        if player_detail:
            print(f"✅ Player detail retrieved: {len(str(player_detail))} characters")
            print(f"📊 Sample data: {str(player_detail)[:200]}...")
        else:
            print("❌ No player detail data")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 3: Team Injuries
    print("3. Testing Team Injuries...")
    try:
        team_id = "22"  # From your example
        team_injuries = nfl_api.get_team_injuries(team_id)
        if team_injuries:
            print(f"✅ Team injuries retrieved: {len(str(team_injuries))} characters")
            print(f"📊 Sample data: {str(team_injuries)[:200]}...")
        else:
            print("❌ No team injuries data")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 4: Player Statistics
    print("4. Testing Player Statistics...")
    try:
        player_id = "15035"  # From your example
        year = 2023
        player_stats = nfl_api.get_player_statistics(player_id, year)
        if player_stats:
            print(f"✅ Player statistics retrieved: {len(str(player_stats))} characters")
            print(f"📊 Sample data: {str(player_stats)[:200]}...")
        else:
            print("❌ No player statistics data")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 5: Team Roster
    print("5. Testing Team Roster...")
    try:
        team_id = "22"  # From your example
        team_roster = nfl_api.get_team_players(team_id)
        if team_roster:
            print(f"✅ Team roster retrieved: {len(str(team_roster))} characters")
            print(f"📊 Sample data: {str(team_roster)[:200]}...")
        else:
            print("❌ No team roster data")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 6: Calendar
    print("6. Testing NFL Calendar...")
    try:
        calendar = nfl_api.get_nfl_calendar_ondays()
        if calendar:
            print(f"✅ Calendar retrieved: {len(str(calendar))} characters")
            print(f"📊 Sample data: {str(calendar)[:200]}...")
        else:
            print("❌ No calendar data")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    print("🏁 API Testing Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_real_api()
