#!/usr/bin/env python3
"""
Real NFL Data CLI Demo - Show how to use real API data in fantasy league
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../app'))

from dotenv import load_dotenv
load_dotenv()

from api_service import nfl_api

def show_live_scores():
    """Show live NFL scores"""
    print("🏈 LIVE NFL SCORES")
    print("=" * 30)
    
    live_data = nfl_api.get_live_scores()
    if not live_data or 'live' not in live_data:
        print("❌ No live games currently")
        return
    
    games = live_data['live']
    print(f"📊 Found {len(games)} live games")
    print()
    
    for i, game in enumerate(games, 1):
        print(f"{i}. {game.get('competitionDisplayName', 'NFL')} - {game.get('roundName', 'Unknown')}")
        print(f"   ⏰ {game.get('startTime', 'Unknown')}")
        print(f"   🏟️  {game.get('venue', {}).get('fullName', 'Unknown')}")
        print(f"   📊 Status: {game.get('statusGroup', 'Unknown')}")
        print()

def show_team_roster(team_id):
    """Show team roster with fantasy-relevant players"""
    print(f"👥 TEAM ROSTER - Team {team_id}")
    print("=" * 40)
    
    roster_data = nfl_api.get_team_players(team_id)
    if not roster_data or 'athletes' not in roster_data:
        print("❌ No roster data found")
        return
    
    athletes = roster_data['athletes']
    print(f"📊 Total players: {len(athletes)}")
    print()
    
    # Group by position
    by_position = {}
    fantasy_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
    
    for athlete in athletes:
        position = athlete.get('position', 'Unknown')
        if isinstance(position, dict):
            position = position.get('displayName', 'Unknown')
        
        if position not in by_position:
            by_position[position] = []
        
        player_info = {
            'name': athlete.get('displayName', 'Unknown'),
            'jersey': athlete.get('jersey', 'Unknown'),
            'height': athlete.get('displayHeight', 'Unknown'),
            'weight': athlete.get('displayWeight', 'Unknown')
        }
        by_position[position].append(player_info)
    
    # Show fantasy-relevant positions first
    for pos in fantasy_positions:
        if pos in by_position:
            players = by_position[pos]
            print(f"🏈 {pos} ({len(players)} players):")
            for player in players[:5]:  # Show first 5
                print(f"   #{player['jersey']} {player['name']} - {player['height']}, {player['weight']}")
            if len(players) > 5:
                print(f"   ... and {len(players) - 5} more")
            print()
    
    # Show other positions
    other_positions = [pos for pos in by_position.keys() if pos not in fantasy_positions]
    if other_positions:
        print("🔧 Other positions:")
        for pos in sorted(other_positions):
            players = by_position[pos]
            print(f"   {pos}: {len(players)} players")

def show_team_injuries(team_id):
    """Show team injuries"""
    print(f"🏥 TEAM INJURIES - Team {team_id}")
    print("=" * 40)
    
    injury_data = nfl_api.get_team_injuries(team_id)
    if not injury_data or 'injuries' not in injury_data:
        print("❌ No injury data found")
        return
    
    injuries = injury_data['injuries']
    print(f"📊 Total injuries: {len(injuries)}")
    print()
    
    # Group by status
    by_status = {}
    for injury in injuries:
        status = injury.get('status', 'Unknown')
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(injury)
    
    for status, injury_list in by_status.items():
        print(f"🤕 {status} ({len(injury_list)} players):")
        for injury in injury_list[:5]:  # Show first 5
            player = injury.get('athlete', 'Unknown')
            injury_type = injury.get('injuryType', 'Unknown')
            comment = injury.get('shortComment', '')
            print(f"   {player} - {injury_type}")
            if comment:
                print(f"     💬 {comment}")
        if len(injury_list) > 5:
            print(f"   ... and {len(injury_list) - 5} more")
        print()

def show_player_detail(player_id):
    """Show detailed player information"""
    print(f"👤 PLAYER DETAIL - ID {player_id}")
    print("=" * 40)
    
    player_data = nfl_api.get_player_detail(player_id)
    if not player_data:
        print("❌ No player data found")
        return
    
    print(f"📊 Data size: {len(str(player_data))} characters")
    print()
    print(f"👤 Name: {player_data.get('displayName', 'Unknown')}")
    print(f"🏈 Position: {player_data.get('position', {}).get('displayName', 'Unknown')}")
    print(f"🏟️  Team: {player_data.get('team', {}).get('displayName', 'Unknown')}")
    print(f"📏 Height: {player_data.get('displayHeight', 'Unknown')}")
    print(f"⚖️  Weight: {player_data.get('displayWeight', 'Unknown')}")
    print(f"🔢 Jersey: #{player_data.get('jersey', 'Unknown')}")
    print(f"🎓 College: {player_data.get('college', {}).get('name', 'Unknown')}")
    print(f"📅 Age: {player_data.get('age', 'Unknown')}")
    print(f"🏆 Experience: {player_data.get('experience', 'Unknown')}")

def show_nfl_calendar():
    """Show NFL calendar"""
    print("📅 NFL CALENDAR")
    print("=" * 20)
    
    calendar = nfl_api.get_nfl_calendar_ondays()
    if not calendar:
        print("❌ No calendar data found")
        return
    
    print(f"📊 Data size: {len(str(calendar))} characters")
    print()
    print(f"📅 Start date: {calendar.get('startDate', 'Unknown')}")
    print(f"📅 End date: {calendar.get('endDate', 'Unknown')}")
    
    if 'eventDate' in calendar and 'dates' in calendar['eventDate']:
        dates = calendar['eventDate']['dates']
        print(f"📆 Total event dates: {len(dates)}")
        print()
        print("📅 Upcoming events:")
        for i, date in enumerate(dates[:10]):  # Show first 10
            print(f"   {i+1}. {date}")
        if len(dates) > 10:
            print(f"   ... and {len(dates) - 10} more")

def main():
    """Main CLI demo"""
    print("🏈 Real NFL Data CLI Demo")
    print("=" * 50)
    print("This demonstrates how to use real NFL API data")
    print("in your fantasy league system.")
    print()
    
    # Show live scores
    show_live_scores()
    
    # Show team roster
    print("\n" + "="*50)
    show_team_roster("22")
    
    # Show team injuries
    print("\n" + "="*50)
    show_team_injuries("22")
    
    # Show player detail
    print("\n" + "="*50)
    show_player_detail("4360644")
    
    # Show calendar
    print("\n" + "="*50)
    show_nfl_calendar()
    
    print("\n" + "="*50)
    print("🏁 CLI Demo Complete!")
    print("=" * 50)
    print("\n💡 This shows real NFL data being processed")
    print("🔧 Ready to integrate into your fantasy league")
    print("📈 All data is live and up-to-date")
    print("\n🚀 Next steps:")
    print("1. Use this data in your fantasy league")
    print("2. Build real-time features")
    print("3. Monitor player injuries")
    print("4. Track live scores")

if __name__ == "__main__":
    main()
