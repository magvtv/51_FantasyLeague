#!/usr/bin/env python3
"""
Real NFL Data Processor - Extract meaningful data from API responses
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

class NFLDataProcessor:
    """Process real NFL API data into fantasy league format"""
    
    def __init__(self):
        self.api = nfl_api
    
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
                'venue': game.get('venue', {}).get('fullName', 'Unknown'),
                'teams': []
            }
            
            # Extract team information
            if 'competitions' in game:
                for comp in game['competitions']:
                    if 'competitors' in comp:
                        for team in comp['competitors']:
                            team_info = {
                                'team_id': team.get('id'),
                                'team_name': team.get('team', {}).get('displayName', 'Unknown'),
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
            'position': player_data.get('position', {}).get('displayName', 'Unknown'),
            'team': player_data.get('team', {}).get('displayName', 'Unknown'),
            'height': player_data.get('displayHeight'),
            'weight': player_data.get('displayWeight'),
            'age': player_data.get('age'),
            'jersey': player_data.get('jersey'),
            'college': player_data.get('college', {}).get('name', 'Unknown'),
            'experience': player_data.get('experience')
        }
    
    def process_team_roster(self, team_id):
        """Process team roster into fantasy-relevant format"""
        roster_data = self.api.get_team_players(team_id)
        if not roster_data or 'athletes' not in roster_data:
            return []
        
        players = []
        for athlete in roster_data['athletes']:
            player = {
                'player_id': athlete.get('id'),
                'name': athlete.get('displayName'),
                'first_name': athlete.get('firstName'),
                'last_name': athlete.get('lastName'),
                'position': athlete.get('position', 'Unknown') if isinstance(athlete.get('position'), str) else athlete.get('position', {}).get('displayName', 'Unknown'),
                'jersey': athlete.get('jersey'),
                'height': athlete.get('displayHeight'),
                'weight': athlete.get('displayWeight'),
                'age': athlete.get('age'),
                'college': athlete.get('college', {}).get('name', 'Unknown'),
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
    
    def process_player_statistics(self, player_id, year=2023):
        """Process player statistics into fantasy-relevant format"""
        stats_data = self.api.get_player_statistics(player_id, year)
        if not stats_data or 'statistics' not in stats_data:
            return None
        
        stats = stats_data['statistics']
        processed_stats = {
            'player_id': player_id,
            'year': year,
            'splits': []
        }
        
        if 'splits' in stats and stats['splits']:
            for split in stats['splits']:
                split_info = {
                    'name': split.get('name', 'Unknown'),
                    'display_name': split.get('displayName', 'Unknown'),
                    'stats': {}
                }
                
                # Extract categories and stats
                if 'categories' in split:
                    for category in split['categories']:
                        category_name = category.get('name', 'Unknown')
                        split_info['stats'][category_name] = {}
                        
                        if 'stats' in category:
                            for stat in category['stats']:
                                stat_name = stat.get('name', 'Unknown')
                                stat_value = stat.get('value', 0)
                                split_info['stats'][category_name][stat_name] = stat_value
                
                processed_stats['splits'].append(split_info)
        
        return processed_stats
    
    def get_fantasy_relevant_players(self, team_id, positions=['QB', 'RB', 'WR', 'TE', 'K']):
        """Get fantasy-relevant players from team roster"""
        roster = self.process_team_roster(team_id)
        fantasy_players = []
        
        for player in roster:
            if player['position'] in positions:
                fantasy_players.append(player)
        
        return fantasy_players
    
    def get_injured_fantasy_players(self, team_id):
        """Get injured fantasy-relevant players"""
        injuries = self.process_team_injuries(team_id)
        fantasy_positions = ['QB', 'RB', 'WR', 'TE', 'K']
        injured_fantasy = []
        
        for injury in injuries:
            # This is a simplified check - in reality you'd match player names
            if any(pos in injury['player_name'] for pos in fantasy_positions):
                injured_fantasy.append(injury)
        
        return injured_fantasy

def main():
    """Demonstrate real data processing"""
    print("🏈 Real NFL Data Processor Demo")
    print("=" * 50)
    
    processor = NFLDataProcessor()
    
    # Process live scores
    print("\n1. PROCESSING LIVE SCORES:")
    games = processor.process_live_scores()
    print(f"✅ Found {len(games)} live games")
    if games:
        game = games[0]
        print(f"🎮 Sample game: {game['competition']} - {game['round']}")
        print(f"⏰ Start time: {game['start_time']}")
        print(f"🏟️  Venue: {game['venue']}")
        print(f"👥 Teams: {len(game['teams'])}")
    
    # Process player detail
    print("\n2. PROCESSING PLAYER DETAIL:")
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
    print("\n3. PROCESSING TEAM ROSTER:")
    team_id = "22"
    roster = processor.process_team_roster(team_id)
    print(f"✅ Found {len(roster)} players")
    
    # Get fantasy-relevant players
    fantasy_players = processor.get_fantasy_relevant_players(team_id)
    print(f"🏈 Fantasy-relevant players: {len(fantasy_players)}")
    
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
    print("\n4. PROCESSING TEAM INJURIES:")
    injuries = processor.process_team_injuries(team_id)
    print(f"🏥 Found {len(injuries)} injuries")
    
    # Process player statistics
    print("\n5. PROCESSING PLAYER STATISTICS:")
    player_id = "15035"
    stats = processor.process_player_statistics(player_id, 2023)
    if stats:
        print(f"✅ Statistics for player {player_id}")
        print(f"📊 Splits available: {len(stats['splits'])}")
    
    print("\n🏁 Data Processing Complete!")
    print("=" * 50)
    print("\n💡 This shows how to extract meaningful data from the API")
    print("🔧 Ready to integrate into your fantasy league system")
    print("📈 Can now build features like:")
    print("   - Live score tracking")
    print("   - Player injury monitoring")
    print("   - Team roster management")
    print("   - Performance statistics")

if __name__ == "__main__":
    main()
