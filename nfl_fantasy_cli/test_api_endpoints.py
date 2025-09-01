#!/usr/bin/env python3
"""
Test script to verify API endpoints work correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from api_service import nfl_api

def test_api_connection():
    """Test basic API connection"""
    print("Testing API connection...")
    
    # Check if API key is set
    if not nfl_api.headers.get("x-rapidapi-key"):
        print("❌ RAPIDAPI_KEY not found in environment variables")
        print("Please set RAPIDAPI_KEY in your .env file")
        return False
    
    print("✅ API key found")
    return True

def test_teams_endpoint():
    """Test teams endpoint"""
    print("\nTesting teams endpoint...")
    
    try:
        teams_data = nfl_api.get_team_data()
        if teams_data and 'teams' in teams_data:
            print(f"✅ Teams endpoint working - Found {len(teams_data['teams'])} teams")
            return True
        else:
            print("❌ Teams endpoint failed - No data returned")
            return False
    except Exception as e:
        print(f"❌ Teams endpoint error: {e}")
        return False

def test_players_endpoint():
    """Test players endpoint"""
    print("\nTesting players endpoint...")
    
    try:
        # Get first team to test players endpoint
        teams_data = nfl_api.get_team_data()
        if not teams_data or 'teams' not in teams_data:
            print("❌ Cannot test players endpoint - No teams data")
            return False
        
        first_team = teams_data['teams'][0]
        team_id = first_team.get('id')
        
        players_data = nfl_api.get_players_by_team(team_id)
        if players_data and 'players' in players_data:
            print(f"✅ Players endpoint working - Found {len(players_data['players'])} players for {first_team.get('name')}")
            return True
        else:
            print("❌ Players endpoint failed - No data returned")
            return False
    except Exception as e:
        print(f"❌ Players endpoint error: {e}")
        return False

def test_season_stats_endpoint():
    """Test season stats endpoint"""
    print("\nTesting season stats endpoint...")
    
    try:
        season_stats = nfl_api.get_season_stats(2024)
        if season_stats and 'players' in season_stats:
            print(f"✅ Season stats endpoint working - Found {len(season_stats['players'])} player records")
            return True
        else:
            print("❌ Season stats endpoint failed - No data returned")
            return False
    except Exception as e:
        print(f"❌ Season stats endpoint error: {e}")
        return False

def test_weekly_stats_endpoint():
    """Test weekly stats endpoint"""
    print("\nTesting weekly stats endpoint...")
    
    try:
        weekly_stats = nfl_api.get_weekly_stats(2024, 1)
        if weekly_stats and 'players' in weekly_stats:
            print(f"✅ Weekly stats endpoint working - Found {len(weekly_stats['players'])} player records for Week 1")
            return True
        else:
            print("❌ Weekly stats endpoint failed - No data returned")
            return False
    except Exception as e:
        print(f"❌ Weekly stats endpoint error: {e}")
        return False

def test_injury_endpoint():
    """Test injury endpoint"""
    print("\nTesting injury endpoint...")
    
    try:
        injury_data = nfl_api.get_injury_report()
        if injury_data:
            print(f"✅ Injury endpoint working - Found {len(injury_data)} injury records")
            return True
        else:
            print("❌ Injury endpoint failed - No data returned")
            return False
    except Exception as e:
        print(f"❌ Injury endpoint error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 NFL Fantasy League API Endpoint Tests")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        test_api_connection,
        test_teams_endpoint,
        test_players_endpoint,
        test_season_stats_endpoint,
        test_weekly_stats_endpoint,
        test_injury_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API endpoints are working correctly.")
    else:
        print("⚠️  Some tests failed. Check your API key and network connection.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

