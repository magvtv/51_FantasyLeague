#!/usr/bin/env python3
"""
Populate NFL Fantasy League database with real NFL players from API
"""

import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from dotenv import load_dotenv
load_dotenv()

from app.database import get_app, get_db
from app.models import NFLPlayer
from app.api_service import nfl_api

def populate_nfl_players():
    """Populate database with real NFL players from API"""
    app = get_app()
    
    with app.app_context():
        db = get_db()
        
        print("🏈 Populating NFL Fantasy League Database with Real Players")
        print("=" * 60)
        
        # NFL team IDs (you can expand this list)
        team_ids = [22, 16, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        
        total_players_added = 0
        
        for team_id in team_ids:
            try:
                print(f"\n📋 Fetching roster for team ID {team_id}...")
                
                # Get team roster from API
                roster_data = nfl_api.get_team_players(team_id)
                
                if not roster_data or 'athletes' not in roster_data:
                    print(f"❌ No roster data for team {team_id}")
                    continue
                
                team_name = roster_data.get('team', {}).get('displayName', f'Team {team_id}')
                print(f"✅ Found {len(roster_data['athletes'])} players for {team_name}")
                
                players_added = 0
                
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
                        
                        # Get team information
                        team_obj = roster_data.get('team', {})
                        if isinstance(team_obj, dict):
                            team_code = team_obj.get('abbreviation', f'TEAM{team_id}')
                        else:
                            team_code = f'TEAM{team_id}'
                        
                        # Only add fantasy-relevant positions
                        fantasy_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'P', 'DL', 'LB', 'CB', 'S']
                        if position_name not in fantasy_positions:
                            continue
                        
                        # Check if player already exists
                        existing_player = NFLPlayer.query.filter_by(nfl_id=player_id).first()
                        if existing_player:
                            continue
                        
                        # Calculate fantasy price based on position and age
                        base_price = calculate_fantasy_price(position_name, age)
                        
                        # Create new player
                        player = NFLPlayer(
                            nfl_id=player_id,
                            name=display_name,
                            first_name=first_name,
                            last_name=last_name,
                            position=position_name,
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
                        
                    except Exception as e:
                        print(f"⚠️  Error processing player {athlete_data.get('displayName', 'Unknown')}: {e}")
                        continue
                
                print(f"✅ Added {players_added} players for {team_name}")
                
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
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'P', 'DL', 'LB', 'CB', 'S']
        for pos in positions:
            count = NFLPlayer.query.filter_by(position=pos).count()
            if count > 0:
                print(f"  {pos}: {count} players")

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
        'S': 2000000
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
    print("NFL Fantasy League Database Population")
    print("=" * 40)
    
    # Ask user if they want to clear existing players
    response = input("Clear existing players first? (y/n): ").lower().strip()
    if response == 'y':
        clear_existing_players()
    
    # Populate with real players
    populate_nfl_players()
    
    print("\n🚀 Ready to use real NFL players in your fantasy league!")
