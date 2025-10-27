#!/usr/bin/env python3
"""
Efficient NFL player population respecting rate limits
Populates one team at a time to avoid hitting API limits
"""

import sys
import os
import time
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from dotenv import load_dotenv
load_dotenv()

from app.database import get_app, get_db
from app.models import NFLPlayer
from app.api_service import nfl_api

def populate_single_team(team_id, team_name=None, team_code=None):
    """Populate database with players from a single NFL team"""
    app = get_app()
    
    with app.app_context():
        db = get_db()
        
        print(f"🏈 Populating players for Team ID: {team_id}")
        print("=" * 40)
        
        try:
            # Get team roster from API
            roster_data = nfl_api.get_team_players(team_id)
            
            if not roster_data or 'athletes' not in roster_data:
                print(f"❌ No roster data for team {team_id}")
                return False
            
            # Extract team info from API response
            api_team_name = roster_data.get('team', {}).get('displayName', team_name or f'Team {team_id}')
            api_team_code = roster_data.get('team', {}).get('abbreviation', team_code or f'TEAM{team_id}')
            
            print(f"✅ Found {len(roster_data['athletes'])} players for {api_team_name} ({api_team_code})")
            
            players_added = 0
            positions_found = set()
            
            for athlete_data in roster_data['athletes']:
                try:
                    # Extract player information
                    player_id = athlete_data.get('id')
                    display_name = athlete_data.get('displayName')
                    first_name = athlete_data.get('firstName')
                    last_name = athlete_data.get('lastName')
                    jersey = athlete_data.get('jersey')
                    height = athlete_data.get('displayHeight')
                    weight = athlete_data.get('displayWeight')
                    age = athlete_data.get('age')
                    
                    # Get position information
                    position_obj = athlete_data.get('position', {})
                    if isinstance(position_obj, dict):
                        position_name = position_obj.get('displayName', 'Unknown')
                    else:
                        position_name = str(position_obj) if position_obj else 'Unknown'
                    
                    positions_found.add(position_name)
                    
                    # Map NFL positions to fantasy positions
                    fantasy_position = map_to_fantasy_position(position_name)
                    if not fantasy_position:
                        continue  # Skip non-fantasy positions
                    
                    # Check if player already exists
                    existing_player = NFLPlayer.query.filter_by(nfl_id=player_id).first()
                    if existing_player:
                        continue
                    
                    # Calculate fantasy price based on position and age
                    base_price = calculate_fantasy_price(fantasy_position, age)
                    
                    # Create new player
                    player = NFLPlayer(
                        nfl_id=player_id,
                        name=display_name,
                        first_name=first_name,
                        last_name=last_name,
                        position=fantasy_position,
                        team=api_team_code,
                        jersey_number=jersey,
                        height=height,
                        weight=weight,
                        age=age,
                        price=base_price,
                        total_points=0.0,
                        is_injured=False,
                        injury_status='Healthy'
                    )
                    
                    db.session.add(player)
                    players_added += 1
                    
                    # Show progress for first few players
                    if players_added <= 5:
                        print(f"  ✅ Added: {display_name} - {fantasy_position} - #{jersey}")
                    
                except Exception as e:
                    print(f"⚠️  Error processing player {athlete_data.get('displayName', 'Unknown')}: {e}")
                    continue
            
            # Commit the team
            db.session.commit()
            
            print(f"✅ Added {players_added} players for {api_team_name}")
            print(f"📊 Positions found: {sorted(positions_found)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing team {team_id}: {e}")
            db.session.rollback()
            return False

def get_team_listing():
    """Get NFL team listing to find correct team IDs"""
    try:
        teams_data = nfl_api.get_team_listing()
        
        if teams_data and 'teams' in teams_data:
            teams = teams_data['teams']
            print(f"📋 Found {len(teams)} NFL teams:")
            print("-" * 50)
            
            for i, team in enumerate(teams):
                team_id = team.get('id')
                team_name = team.get('displayName', 'Unknown')
                team_code = team.get('abbreviation', 'Unknown')
                print(f"{i+1:2d}. ID: {team_id:2d} | {team_name:25s} | {team_code}")
            
            return teams
        else:
            print("❌ Could not get team listing")
            return None
            
    except Exception as e:
        print(f"❌ Error getting team listing: {e}")
        return None

def map_to_fantasy_position(nfl_position):
    """Map NFL position to fantasy position"""
    position_mapping = {
        # Quarterbacks
        'QB': 'QB',
        'Quarterback': 'QB',
        
        # Running Backs
        'RB': 'RB',
        'Running Back': 'RB',
        'HB': 'RB',  # Halfback
        'FB': 'RB',  # Fullback
        
        # Wide Receivers
        'WR': 'WR',
        'Wide Receiver': 'WR',
        
        # Tight Ends
        'TE': 'TE',
        'Tight End': 'TE',
        
        # Kickers
        'K': 'K',
        'Kicker': 'K',
        
        # Punters
        'P': 'P',
        'Punter': 'P',
        'LS': 'P',   # Long Snapper
        
        # Defense - Line
        'DE': 'DL',  # Defensive End
        'DT': 'DL',  # Defensive Tackle
        'NT': 'DL',  # Nose Tackle
        
        # Defense - Linebackers
        'LB': 'LB',
        'OLB': 'LB',  # Outside Linebacker
        'ILB': 'LB',  # Inside Linebacker
        'MLB': 'LB',  # Middle Linebacker
        
        # Defense - Secondary
        'CB': 'CB',  # Cornerback
        'S': 'S',    # Safety
        'FS': 'S',   # Free Safety
        'SS': 'S',   # Strong Safety
        'DB': 'CB',  # Defensive Back
    }
    
    return position_mapping.get(nfl_position, None)

def calculate_fantasy_price(position, age):
    """Calculate fantasy price based on position and age"""
    base_prices = {
        'QB': 5000000,
        'RB': 4000000,
        'WR': 3500000,
        'TE': 3000000,
        'K': 1000000,
        'P': 500000,
        'DL': 2000000,
        'LB': 2500000,
        'CB': 2000000,
        'S': 2000000,
        'DEF': 3000000
    }
    
    base_price = base_prices.get(position, 1000000)
    
    # Adjust for age
    if age and 25 <= age <= 30:
        return int(base_price * 1.2)  # Prime years
    elif age and age < 25:
        return int(base_price * 0.9)  # Young players
    elif age and age > 30:
        return int(base_price * 0.8)  # Veterans
    else:
        return base_price

def show_database_summary():
    """Show current database summary"""
    app = get_app()
    
    with app.app_context():
        total_players = NFLPlayer.query.count()
        print(f"\n📊 Database Summary:")
        print(f"Total players: {total_players}")
        
        if total_players > 0:
            print("\nPlayers by position:")
            positions = ['QB', 'RB', 'WR', 'TE', 'K', 'P', 'DL', 'LB', 'CB', 'S', 'DEF']
            for pos in positions:
                count = NFLPlayer.query.filter_by(position=pos).count()
                if count > 0:
                    print(f"  {pos}: {count} players")
            
            print("\nSample QBs:")
            qbs = NFLPlayer.query.filter_by(position='QB').limit(5).all()
            for qb in qbs:
                print(f"  - {qb.name} ({qb.team}) - \${qb.price:,.0f}")

if __name__ == "__main__":
    print("NFL Fantasy League - Efficient Player Population")
    print("=" * 50)
    print("Rate Limit: 1000 requests/hour")
    print("Strategy: Populate one team at a time")
    print()
    
    # Show current database status
    show_database_summary()
    
    print("\nOptions:")
    print("1. Get team listing (uses 1 API call)")
    print("2. Populate specific team (uses 1 API call)")
    print("3. Show database summary")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🏈 Getting NFL Team Listing...")
        teams = get_team_listing()
        if teams:
            print(f"\n✅ Found {len(teams)} teams. Use team IDs to populate specific teams.")
    
    elif choice == "2":
        team_id = input("Enter team ID to populate: ").strip()
        if team_id.isdigit():
            print(f"\n🏈 Populating team ID {team_id}...")
            success = populate_single_team(int(team_id))
            if success:
                print("✅ Team populated successfully!")
                show_database_summary()
            else:
                print("❌ Failed to populate team")
        else:
            print("❌ Invalid team ID")
    
    elif choice == "3":
        show_database_summary()
    
    else:
        print("❌ Invalid choice")
    
    print("\n💡 Tip: With rate limits, populate teams gradually over time")
    print("   Each team population uses only 1 API call")
