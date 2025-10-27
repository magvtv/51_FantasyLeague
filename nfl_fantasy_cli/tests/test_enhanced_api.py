#!/usr/bin/env python3
"""
Enhanced NFL Fantasy League API Test Script
Tests all the new API endpoints and functionality
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.api_service import nfl_api

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(title, result, show_data=False):
    """Print formatted result"""
    print(f"\n{title}:")
    if result:
        if isinstance(result, dict):
            if result.get('success'):
                print(f"  ✅ Success: {result.get('message', 'Operation completed')}")
                if show_data and 'data' in result:
                    print(f"  📊 Data: {len(str(result['data']))} characters")
            else:
                print(f"  ❌ Failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"  📊 Data: {len(str(result))} characters")
            if show_data:
                print(f"  Raw data: {result}")
    else:
        print("  ❌ No data returned")

def test_basic_endpoints():
    """Test basic API endpoints"""
    print_section("BASIC API ENDPOINTS")
    
    # Test live scores
    print_result("Live Scores", nfl_api.get_live_scores())
    
    # Test calendar
    print_result("NFL Calendar", nfl_api.get_nfl_calendar_ondays())
    
    # Test teams
    teams = nfl_api.get_teams_list()
    print_result("Teams List", teams)
    
    return teams

def test_player_endpoints():
    """Test player-related endpoints"""
    print_section("PLAYER ENDPOINTS")
    
    # Test player detail (using a sample player ID)
    player_id = "4360644"  # Example player ID from your list
    print_result(f"Player Detail (ID: {player_id})", nfl_api.get_player_detail(player_id))
    
    # Test player statistics
    print_result(f"Player Statistics (ID: {player_id}, 2023)", 
                nfl_api.get_player_statistics(player_id, 2023))
    
    # Test player overview
    print_result(f"Player Overview (ID: {player_id})", 
                nfl_api.get_player_overview(player_id))
    
    # Test player standings
    print_result(f"Player Standings (ID: {player_id})", 
                nfl_api.get_player_standings(player_id))

def test_team_endpoints(teams):
    """Test team-related endpoints"""
    print_section("TEAM ENDPOINTS")
    
    if teams and len(teams) > 0:
        team_id = teams[0].get('id')
        team_name = teams[0].get('name', 'Unknown')
        
        print(f"Testing with team: {team_name} (ID: {team_id})")
        
        # Test team injuries
        print_result(f"Team Injuries (ID: {team_id})", 
                    nfl_api.get_team_injuries(team_id))
        
        # Test team roster
        print_result(f"Team Roster (ID: {team_id})", 
                    nfl_api.get_team_players(team_id))
        
        # Test team statistics
        print_result(f"Team Statistics (ID: {team_id}, 2023)", 
                    nfl_api.get_team_statistics(team_id, 2023))
    else:
        print("No teams available for testing")

def test_coach_endpoints():
    """Test coach-related endpoints"""
    print_section("COACH ENDPOINTS")
    
    # Test coach details (using a sample coach ID)
    coach_id = "17587"  # Example coach ID from your list
    print_result(f"Coach Details (ID: {coach_id})", 
                nfl_api.get_coach_details(coach_id))

def test_sync_methods():
    """Test data sync methods"""
    print_section("DATA SYNC METHODS")
    
    # Test live scores sync
    print_result("Sync Live Scores", nfl_api.sync_live_scores_to_db())
    
    # Test player details sync
    player_id = "4360644"
    print_result(f"Sync Player Details (ID: {player_id})", 
                nfl_api.sync_player_details_to_db(player_id))
    
    # Test team injuries sync
    teams = nfl_api.get_teams_list()
    if teams and len(teams) > 0:
        team_id = teams[0].get('id')
        print_result(f"Sync Team Injuries (ID: {team_id})", 
                    nfl_api.sync_team_injuries_to_db(team_id))

def test_analysis_methods():
    """Test analysis methods"""
    print_section("ANALYSIS METHODS")
    
    # Test player analysis
    player_id = "4360644"
    print_result(f"Player Analysis (ID: {player_id})", 
                nfl_api.get_player_fantasy_analysis(player_id))
    
    # Test team analysis
    teams = nfl_api.get_teams_list()
    if teams and len(teams) > 0:
        team_id = teams[0].get('id')
        print_result(f"Team Analysis (ID: {team_id})", 
                    nfl_api.get_team_fantasy_analysis(team_id))
    
    # Test game status
    print_result("Current Game Status", nfl_api.get_current_game_status())

def test_bulk_sync_methods():
    """Test bulk sync methods"""
    print_section("BULK SYNC METHODS")
    
    # Test sync all rosters
    print_result("Sync All Rosters", nfl_api.sync_all_team_rosters())
    
    # Test sync all injuries
    print_result("Sync All Injuries", nfl_api.sync_all_team_injuries())
    
    # Test sync all team stats
    print_result("Sync All Team Stats (2023)", nfl_api.sync_all_team_stats(2023))

def test_cache_info():
    """Test cache information"""
    print_section("CACHE INFORMATION")
    
    cache_info = nfl_api.get_cache_info()
    print(f"Cache Size: {cache_info['size']}")
    print(f"Max Size: {cache_info['maxsize']}")
    print(f"TTL: {cache_info['ttl']} seconds")

def main():
    """Main test function"""
    print("NFL Fantasy League API Test Suite")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Check if API key is configured
    if not os.getenv('RAPIDAPI_KEY'):
        print("\n❌ RAPIDAPI_KEY not found in environment variables")
        print("Please set your RapidAPI key before running tests")
        return
    
    try:
        # Run all tests
        teams = test_basic_endpoints()
        test_player_endpoints()
        test_team_endpoints(teams)
        test_coach_endpoints()
        test_sync_methods()
        test_analysis_methods()
        test_bulk_sync_methods()
        test_cache_info()
        
        print_section("TEST SUMMARY")
        print("✅ All tests completed!")
        print("📊 Check the results above for endpoint availability")
        print("🔧 Some endpoints may return placeholder data if not available")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
