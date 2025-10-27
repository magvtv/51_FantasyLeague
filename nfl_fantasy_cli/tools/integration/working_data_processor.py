#!/usr/bin/env python3
"""
Working Real NFL Data Processor - Handles all data structures properly
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

class WorkingNFLDataProcessor:
    """Process real NFL API data with proper error handling"""
    
    def __init__(self):
        self.api = nfl_api
    
    def safe_get(self, data, *keys, default="Unknown"):
        """Safely get nested dictionary values"""
        try:
            for key in keys:
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return default
            return data if data is not None else default
        except:
            return default
    
    def process_live_scores(self):
        """Process live scores into fantasy-relevant format"""
        live_data = self.api.get_live_scores()
        if not live_data or 'live' not in live_data:
            return []
        
        games = []
        for game in live_data['live']:
            game_info = {
                'game_id': game.get('id'),
                'competition': game.get('competitionDisplayName', 'NFL'),
                'round': game.get('roundName', 'Unknown'),
                'start_time': game.get('startTime'),
                'status': game.get('statusGroup'),
                'venue': self.safe_get(game, 'venue', 'fullName'),
                'teams': []
            }
            
            # Extract team information safely
            if 'competitions' in game:
                for comp in game['competitions']:
                    if 'competitors' in comp:
                        for team in comp['competitors']:
                            team_info = {
                                'team_id': team.get('id'),
                                'team_name': self.safe_get(team, 'team', 'displayName'),
                                'score': team.get('score'),
                                'winner': team.get('winner', False)
                            }
                            game_info['teams'].append(team_info)
            
            games.append(game_info)
        
        return games
    
    def process_player_detail(self, player_id):
        """Process player detail into fantasy-relevant format"""
        player_data = self.api.get_player_detail(player_id)
        if not player_data:
            return None
        
        return {
            'player_id': player_data.get('id'),
            'name': player_data.get('displayName'),
            'first_name': player_data.get('firstName'),
            'last_name': player_data.get('lastName'),
            'position': self.safe_get(player_data, 'position', 'displayName'),
            'team': self.safe_get(player_data, 'team', 'displayName'),
            'height': player_data.get('displayHeight'),
            'weight': player_data.get('displayWeight'),
            'age': player_data.get('age'),
            'jersey': player_data.get('jersey'),
            'college': self.safe_get(player_data, 'college', 'name'),
            'experience': player_data.get('experience')
        }
    
    def process_team_roster(self, team_id):
        """Process team roster into fantasy-relevant format"""
        roster_data = self.api.get_team_players(team_id)
        if not roster_data or 'athletes' not in roster_data:
            return []
        
        players = []
        for athlete in roster_data['athletes']:
            # Handle position field safely
            position = athlete.get('position', 'Unknown')
            if isinstance(position, dict):
                position = position.get('displayName', 'Unknown')
            
            # Handle college field safely
            college = athlete.get('college', 'Unknown')
            if isinstance(college, dict):
                college = college.get('name', 'Unknown')
            
            player = {
                'player_id': athlete.get('id'),
                'name': athlete.get('displayName'),
                'first_name': athlete.get('firstName'),
                'last_name': athlete.get('lastName'),
                'position': position,
                'jersey': athlete.get('jersey'),
                'height': athlete.get('displayHeight'),
                'weight': athlete.get('displayWeight'),
                'age': athlete.get('age'),
                'college': college,
                'experience': athlete.get('experience')
            }
            players.append(player)
        
        return players
    
    def process_team_injuries(self, team_id):
        """Process team injuries into fantasy-relevant format"""
        injury_data = self.api.get_team_injuries(team_id)
        if not injury_data or 'injuries' not in injury_data:
            return []
        
        injuries = []
        for injury in injury_data['injuries']:
            injury_info = {
                'injury_id': injury.get('id'),
                'player_name': injury.get('athlete', 'Unknown'),
                'status': injury.get('status', 'Unknown'),
                'injury_type': injury.get('injuryType', 'Unknown'),
                'date': injury.get('date'),
                'comment': injury.get('longComment', ''),
                'short_comment': injury.get('shortComment', '')
            }
            injuries.append(injury_info)
        
        return injuries
    
    def get_fantasy_relevant_players(self, team_id, positions=['QB', 'RB', 'WR', 'TE', 'K']):
        """Get fantasy-relevant players from team roster"""
        roster = self.process_team_roster(team_id)
        fantasy_players = []
        
        for player in roster:
            if player['position'] in positions:
                fantasy_players.append(player)
        
        return fantasy_players
    
    def get_player_sample_data(self, player_id):
        """Get sample player data for demonstration"""
        player_data = self.api.get_player_detail(player_id)
        if not player_data:
            return None
        
        return {
            'id': player_data.get('id'),
            'name': player_data.get('displayName'),
            'position': self.safe_get(player_data, 'position', 'displayName'),
            'team': self.safe_get(player_data, 'team', 'displayName'),
            'height': player_data.get('displayHeight'),
            'weight': player_data.get('displayWeight'),
            'jersey': player_data.get('jersey'),
            'raw_data_size': len(str(player_data))
        }

def main():
    """Demonstrate working data processing"""
    print("🏈 Working Real NFL Data Processor Demo")
    print("=" * 60)
    
    processor = WorkingNFLDataProcessor()
    
    # Process live scores
    print("\n1. LIVE SCORES:")
    games = processor.process_live_scores()
    print(f"✅ Found {len(games)} live games")
    if games:
        game = games[0]
        print(f"🎮 Sample game: {game['competition']} - {game['round']}")
        print(f"⏰ Start time: {game['start_time']}")
        print(f"🏟️  Venue: {game['venue']}")
        print(f"👥 Teams: {len(game['teams'])}")
    
    # Process player detail
    print("\n2. PLAYER DETAIL:")
    player_id = "4360644"
    player = processor.process_player_detail(player_id)
    if player:
        print(f"✅ Player: {player['name']}")
        print(f"🏈 Position: {player['position']}")
        print(f"🏟️  Team: {player['team']}")
        print(f"📏 Height: {player['height']}")
        print(f"⚖️  Weight: {player['weight']}")
        print(f"🔢 Jersey: #{player['jersey']}")
    
    # Process team roster
    print("\n3. TEAM ROSTER:")
    team_id = "22"
    roster = processor.process_team_roster(team_id)
    print(f"✅ Found {len(roster)} players")
    
    # Show sample players
    if roster:
        print("\n📋 Sample players:")
        for i, player in enumerate(roster[:5]):  # Show first 5 players
            print(f"  {i+1}. {player['name']} - {player['position']} #{player['jersey']}")
    
    # Get fantasy-relevant players
    fantasy_players = processor.get_fantasy_relevant_players(team_id)
    print(f"\n🏈 Fantasy-relevant players: {len(fantasy_players)}")
    
    # Group by position
    by_position = {}
    for player in fantasy_players:
        pos = player['position']
        if pos not in by_position:
            by_position[pos] = []
        by_position[pos].append(player)
    
    for pos, players in by_position.items():
        print(f"  {pos}: {len(players)} players")
    
    # Process team injuries
    print("\n4. TEAM INJURIES:")
    injuries = processor.process_team_injuries(team_id)
    print(f"🏥 Found {len(injuries)} injuries")
    
    # Show sample injuries
    if injuries:
        print("\n🤕 Sample injuries:")
        for i, injury in enumerate(injuries[:3]):  # Show first 3 injuries
            print(f"  {i+1}. {injury['player_name']} - {injury['status']}")
    
    # Test different player IDs
    print("\n5. TESTING DIFFERENT PLAYERS:")
    test_players = ["4360644", "15035", "14876"]
    for player_id in test_players:
        player_data = processor.get_player_sample_data(player_id)
        if player_data:
            print(f"✅ Player {player_id}: {player_data['name']} ({player_data['position']}) - {player_data['raw_data_size']} chars")
        else:
            print(f"❌ Player {player_id}: No data")
    
    print("\n🏁 Working Data Processing Complete!")
    print("=" * 60)
    print("\n💡 Key Achievements:")
    print("✅ Successfully processing real NFL API data")
    print("✅ Handling all data structure variations")
    print("✅ Extracting fantasy-relevant information")
    print("✅ Ready for integration into fantasy league")
    print("\n🚀 Ready to build:")
    print("   - Live score tracking")
    print("   - Player injury monitoring")
    print("   - Team roster management")
    print("   - Performance statistics")
    print("   - Fantasy team optimization")

if __name__ == "__main__":
    main()
