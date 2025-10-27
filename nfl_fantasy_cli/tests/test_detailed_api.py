#!/usr/bin/env python3
"""
Detailed Real API Test - Show actual data structure
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

def print_json_data(title, data, max_length=500):
    """Print formatted JSON data"""
    print(f"\n{title}")
    print("=" * len(title))
    if data:
        json_str = json.dumps(data, indent=2)
        if len(json_str) > max_length:
            print(json_str[:max_length] + "...")
            print(f"\n[Data truncated - Full length: {len(json_str)} characters]")
        else:
            print(json_str)
    else:
        print("No data returned")

def test_detailed_api():
    """Test API with detailed output"""
    print("🏈 Detailed NFL API Test")
    print("=" * 50)
    
    # Test 1: Live Scores - Show structure
    print("\n1. LIVE SCORES STRUCTURE:")
    live_scores = nfl_api.get_live_scores()
    if live_scores:
        print(f"✅ Retrieved {len(str(live_scores))} characters")
        if 'live' in live_scores:
            print(f"📊 Found {len(live_scores['live'])} live games")
            if live_scores['live']:
                game = live_scores['live'][0]
                print(f"🎮 Sample game: {game.get('competitionDisplayName', 'NFL')} - {game.get('roundName', 'Unknown')}")
                print(f"⏰ Start time: {game.get('startTime', 'Unknown')}")
                print(f"🏟️  Venue: {game.get('venue', {}).get('fullName', 'Unknown')}")
        print_json_data("Live Scores Data", live_scores, 300)
    
    # Test 2: Player Detail - Show structure
    print("\n2. PLAYER DETAIL STRUCTURE:")
    player_id = "4360644"
    player_detail = nfl_api.get_player_detail(player_id)
    if player_detail:
        print(f"✅ Retrieved {len(str(player_detail))} characters")
        print(f"👤 Player: {player_detail.get('firstName', '')} {player_detail.get('lastName', '')}")
        print(f"🏈 Position: {player_detail.get('position', {}).get('displayName', 'Unknown')}")
        print(f"🏟️  Team: {player_detail.get('team', {}).get('displayName', 'Unknown')}")
        print_json_data("Player Detail Data", player_detail, 400)
    
    # Test 3: Team Injuries - Show structure
    print("\n3. TEAM INJURIES STRUCTURE:")
    team_id = "22"
    team_injuries = nfl_api.get_team_injuries(team_id)
    if team_injuries:
        print(f"✅ Retrieved {len(str(team_injuries))} characters")
        if 'injuries' in team_injuries:
            print(f"🏥 Found {len(team_injuries['injuries'])} injuries")
            if team_injuries['injuries']:
                injury = team_injuries['injuries'][0]
                athlete = injury.get('athlete', {})
                status = injury.get('status', {})
                print(f"👤 Injured player: {athlete.get('displayName', 'Unknown') if isinstance(athlete, dict) else str(athlete)}")
                print(f"🤕 Status: {status.get('displayName', 'Unknown') if isinstance(status, dict) else str(status)}")
        print_json_data("Team Injuries Data", team_injuries, 300)
    
    # Test 4: Team Roster - Show structure
    print("\n4. TEAM ROSTER STRUCTURE:")
    team_roster = nfl_api.get_team_players(team_id)
    if team_roster:
        print(f"✅ Retrieved {len(str(team_roster))} characters")
        if 'athletes' in team_roster:
            print(f"👥 Found {len(team_roster['athletes'])} players")
            if team_roster['athletes']:
                player = team_roster['athletes'][0]
                print(f"👤 Sample player: {player.get('firstName', '')} {player.get('lastName', '')}")
                print(f"🏈 Position: {player.get('position', {}).get('displayName', 'Unknown')}")
                print(f"🔢 Jersey: #{player.get('jersey', 'Unknown')}")
        print_json_data("Team Roster Data", team_roster, 300)
    
    # Test 5: Player Statistics - Show structure
    print("\n5. PLAYER STATISTICS STRUCTURE:")
    player_id = "15035"
    year = 2023
    player_stats = nfl_api.get_player_statistics(player_id, year)
    if player_stats:
        print(f"✅ Retrieved {len(str(player_stats))} characters")
        if 'statistics' in player_stats:
            stats = player_stats['statistics']
            print(f"📊 Statistics available: {len(stats.get('splits', []))} splits")
            if stats.get('splits'):
                split = stats['splits'][0]
                print(f"📈 Sample split: {split.get('name', 'Unknown')}")
        print_json_data("Player Statistics Data", player_stats, 300)
    
    # Test 6: Calendar - Show structure
    print("\n6. NFL CALENDAR STRUCTURE:")
    calendar = nfl_api.get_nfl_calendar_ondays()
    if calendar:
        print(f"✅ Retrieved {len(str(calendar))} characters")
        print(f"📅 Date range: {calendar.get('startDate', 'Unknown')} to {calendar.get('endDate', 'Unknown')}")
        if 'eventDate' in calendar and 'dates' in calendar['eventDate']:
            print(f"📆 Found {len(calendar['eventDate']['dates'])} event dates")
        print_json_data("Calendar Data", calendar, 200)
    
    print("\n🏁 Detailed API Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_detailed_api()
