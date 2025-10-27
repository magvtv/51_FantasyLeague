#!/usr/bin/env python3
"""
Populate NFL Fantasy League database with real NFL players from API
Fixed version with proper position mapping and rate limiting
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

def populate_nfl_players_fixed():
    """Populate database with real NFL players from API - fixed version"""
    app = get_app()
    
    with app.app_context():
        db = get_db()
        
        print("🏈 Populating NFL Fantasy League Database with Real Players (Fixed)")
        print("=" * 70)
        
        # Start with just a few teams to avoid rate limiting
        team_ids = [22, 16, 1, 2, 3]  # Start with 5 teams
        
        total_players_added = 0
        
        for i, team_id in enumerate(team_ids):
            try:
                print(f"\n📋 Fetching roster for team ID {team_id}...")
                
                # Add delay between requests to avoid rate limiting
                if i > 0:
                    print("⏳ Waiting 2 seconds to avoid rate limiting...")
                    time.sleep(2)
                
                # Get team roster from API
                roster_data = nfl_api.get_team_players(team_id)
                
                if not roster_data or 'athletes' not in roster_data:
                    print(f"❌ No roster data for team {team_id}")
                    continue
                
                team_name = roster_data.get('team', {}).get('displayName', f'Team {team_id}')
                team_code = roster_data.get('team', {}).get('abbreviation', f'TEAM{team_id}')
                print(f"✅ Found {len(roster_data['athletes'])} players for {team_name} ({team_code})")
                
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
                        
                        # Get position information - handle different formats
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
                            team=team_code,
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
                        total_players_added += 1
                        
                        # Show progress for first few players
                        if players_added <= 5:
                            print(f"  ✅ Added: {display_name} - {fantasy_position} - {team_code}")
                        
                    except Exception as e:
                        print(f"⚠️  Error processing player {athlete_data.get('displayName', 'Unknown')}: {e}")
                        continue
                
                print(f"✅ Added {players_added} players for {team_name}")
                print(f"📊 Positions found: {sorted(positions_found)}")
                
                # Commit after each team to avoid large transactions
                db.session.commit()
                
            except Exception as e:
                print(f"❌ Error processing team {team_id}: {e}")
                db.session.rollback()
                continue
        
        print(f"\n🎉 Database population complete!")
        print(f"📊 Total players added: {total_players_added}")
        
        # Show summary by position
        print("\n📈 Summary by position:")
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'P', 'DL', 'LB', 'CB', 'S', 'DEF']
        for pos in positions:
            count = NFLPlayer.query.filter_by(position=pos).count()
            if count > 0:
                print(f"  {pos}: {count} players")

def map_to_fantasy_position(nfl_position):
    """Map NFL position to fantasy position"""
    # Common NFL position mappings
    position_mapping = {
        # Quarterbacks
        'QB': 'QB',
        'Quarterback': 'QB',
        
        # Running Backs
        'RB': 'RB',
        'Running Back': 'RB',
        'HB': 'RB',  # Halfback
        
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
        
        # Defense - Line
        'DE': 'DL',  # Defensive End
        'DT': 'DL',  # Defensive Tackle
        'NT': 'DL',  # Nose Tackle
        'DL': 'DL',  # Defensive Line
        
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
        'DB': 'CB',  # Defensive Back (usually cornerback)
        
        # Special cases
        'FB': 'RB',  # Fullback -> Running Back
        'LS': 'P',   # Long Snapper -> Punter
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
    
    # Adjust for age (prime years 25-30 get premium)
    if age and 25 <= age <= 30:
        return int(base_price * 1.2)
    elif age and age < 25:
        return int(base_price * 0.9)  # Rookies/young players cheaper
    elif age and age > 30:
        return int(base_price * 0.8)  # Veterans cheaper
    else:
        return base_price

def clear_existing_players():
    """Clear existing mock players"""
    app = get_app()
    
    with app.app_context():
        db = get_db()
        
        print("🗑️  Clearing existing mock players...")
        
        # Delete all existing players
        NFLPlayer.query.delete()
        db.session.commit()
        
        print("✅ Existing players cleared")

if __name__ == "__main__":
    print("NFL Fantasy League Database Population (Fixed)")
    print("=" * 50)
    
    # Clear existing players automatically
    clear_existing_players()
    
    # Populate with real players
    populate_nfl_players_fixed()
    
    print("\n🚀 Ready to use real NFL players in your fantasy league!")
