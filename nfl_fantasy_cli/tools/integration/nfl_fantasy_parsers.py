#!/usr/bin/env python3
"""
NFL Fantasy League JSON Parsers
Create structured parsers that extract exactly what we need for fantasy league
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../app'))

from dotenv import load_dotenv
load_dotenv()

from api_service import nfl_api

class NFLFantasyParsers:
    """Structured parsers for NFL API data specifically for fantasy league use"""
    
    def __init__(self):
        self.api = nfl_api
    
    def parse_live_scores(self) -> List[Dict[str, Any]]:
        """Parse live scores into fantasy-relevant format"""
        live_data = self.api.get_live_scores()
        if not live_data or 'live' not in live_data:
            return []
        
        games = []
        for game in live_data['live']:
            # Extract basic game info
            game_info = {
                'game_id': game.get('id'),
                'competition': game.get('competitionDisplayName', 'NFL'),
                'round': game.get('roundName', 'Unknown'),
                'start_time': game.get('startTime'),
                'status': game.get('statusText', 'Unknown'),
                'game_time': game.get('gameTime'),
                'just_ended': game.get('justEnded', False),
                'teams': []
            }
            
            # Extract team information
            if 'homeCompetitor' in game:
                home = game['homeCompetitor']
                game_info['teams'].append({
                    'team_id': home.get('id'),
                    'name': home.get('name'),
                    'short_name': home.get('shortName'),
                    'score': home.get('score'),
                    'is_winner': home.get('isWinner', False),
                    'is_home': True
                })
            
            if 'awayCompetitor' in game:
                away = game['awayCompetitor']
                game_info['teams'].append({
                    'team_id': away.get('id'),
                    'name': away.get('name'),
                    'short_name': away.get('shortName'),
                    'score': away.get('score'),
                    'is_winner': away.get('isWinner', False),
                    'is_home': False
                })
            
            games.append(game_info)
        
        return games
    
    def parse_player_detail(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Parse player detail into fantasy-relevant format"""
        player_data = self.api.get_player_detail(player_id)
        if not player_data:
            return None
        
        # Extract basic player info
        player_info = {
            'player_id': player_data.get('id'),
            'name': player_data.get('displayName'),
            'first_name': player_data.get('firstName'),
            'last_name': player_data.get('lastName'),
            'jersey': player_data.get('jersey'),
            'height': player_data.get('displayHeight'),
            'weight': player_data.get('displayWeight'),
            'age': player_data.get('age'),
            'date_of_birth': player_data.get('dateOfBirth'),
            'active': player_data.get('active', False),
            'experience_years': None,
            'birth_place': {},
            'status': {}
        }
        
        # Extract experience
        if 'experience' in player_data and isinstance(player_data['experience'], dict):
            player_info['experience_years'] = player_data['experience'].get('years')
        
        # Extract birth place
        if 'birthPlace' in player_data and isinstance(player_data['birthPlace'], dict):
            birth_place = player_data['birthPlace']
            player_info['birth_place'] = {
                'city': birth_place.get('city'),
                'state': birth_place.get('state'),
                'country': birth_place.get('country')
            }
        
        # Extract status
        if 'status' in player_data and isinstance(player_data['status'], dict):
            status = player_data['status']
            player_info['status'] = {
                'name': status.get('name'),
                'type': status.get('type'),
                'abbreviation': status.get('abbreviation')
            }
        
        return player_info
    
    def parse_team_roster(self, team_id: str) -> List[Dict[str, Any]]:
        """Parse team roster into fantasy-relevant format"""
        roster_data = self.api.get_team_players(team_id)
        if not roster_data or 'athletes' not in roster_data:
            return []
        
        players = []
        for athlete in roster_data['athletes']:
            # Extract basic player info
            player_info = {
                'player_id': athlete.get('id'),
                'name': athlete.get('displayName'),
                'first_name': athlete.get('firstName'),
                'last_name': athlete.get('lastName'),
                'jersey': athlete.get('jersey'),
                'position': athlete.get('position', 'Unknown'),
                'height': athlete.get('displayHeight'),
                'weight': athlete.get('displayWeight'),
                'age': athlete.get('age'),
                'date_of_birth': athlete.get('dateOfBirth'),
                'active': athlete.get('active', False),
                'college': {},
                'experience_years': None,
                'status': {}
            }
            
            # Extract college info
            if 'college' in athlete and isinstance(athlete['college'], dict):
                college = athlete['college']
                player_info['college'] = {
                    'name': college.get('name'),
                    'short_name': college.get('shortName'),
                    'abbreviation': college.get('abbrev'),
                    'mascot': college.get('mascot')
                }
            
            # Extract experience
            if 'experience' in athlete and isinstance(athlete['experience'], dict):
                player_info['experience_years'] = athlete['experience'].get('years')
            
            # Extract status
            if 'status' in athlete and isinstance(athlete['status'], dict):
                status = athlete['status']
                player_info['status'] = {
                    'name': status.get('name'),
                    'type': status.get('type'),
                    'abbreviation': status.get('abbreviation')
                }
            
            players.append(player_info)
        
        return players
    
    def parse_team_injuries(self, team_id: str) -> List[Dict[str, Any]]:
        """Parse team injuries into fantasy-relevant format"""
        injury_data = self.api.get_team_injuries(team_id)
        if not injury_data or 'injuries' not in injury_data:
            return []
        
        injuries = []
        for injury in injury_data['injuries']:
            injury_info = {
                'injury_id': injury.get('id'),
                'status': injury.get('status'),
                'date': injury.get('date'),
                'long_comment': injury.get('longComment', ''),
                'short_comment': injury.get('shortComment', ''),
                'source': {},
                'injury_type': {}
            }
            
            # Extract source info
            if 'source' in injury and isinstance(injury['source'], dict):
                source = injury['source']
                injury_info['source'] = {
                    'description': source.get('description'),
                    'state': source.get('state')
                }
            
            # Extract injury type
            if 'type' in injury and isinstance(injury['type'], dict):
                injury_type = injury['type']
                injury_info['injury_type'] = {
                    'name': injury_type.get('name'),
                    'description': injury_type.get('description'),
                    'abbreviation': injury_type.get('abbreviation')
                }
            
            injuries.append(injury_info)
        
        return injuries
    
    def parse_player_statistics(self, player_id: str, year: int = 2023) -> Optional[Dict[str, Any]]:
        """Parse player statistics into fantasy-relevant format"""
        stats_data = self.api.get_player_statistics(player_id, year)
        if not stats_data or 'statistics' not in stats_data:
            return None
        
        stats = stats_data['statistics']
        parsed_stats = {
            'player_id': player_id,
            'year': year,
            'splits': []
        }
        
        if 'splits' in stats and stats['splits']:
            for split in stats['splits']:
                split_info = {
                    'id': split.get('id'),
                    'name': split.get('name'),
                    'display_name': split.get('displayName'),
                    'abbreviation': split.get('abbreviation'),
                    'type': split.get('type'),
                    'categories': []
                }
                
                # Extract categories
                if 'categories' in split and split['categories']:
                    for category in split['categories']:
                        category_info = {
                            'name': category.get('name'),
                            'display_name': category.get('displayName'),
                            'short_display_name': category.get('shortDisplayName'),
                            'abbreviation': category.get('abbreviation'),
                            'stats': []
                        }
                        
                        # Extract stats
                        if 'stats' in category and category['stats']:
                            for stat in category['stats']:
                                stat_info = {
                                    'name': stat.get('name'),
                                    'display_name': stat.get('displayName'),
                                    'short_display_name': stat.get('shortDisplayName'),
                                    'value': stat.get('value'),
                                    'abbreviation': stat.get('abbreviation')
                                }
                                category_info['stats'].append(stat_info)
                        
                        split_info['categories'].append(category_info)
                
                parsed_stats['splits'].append(split_info)
        
        return parsed_stats
    
    def parse_calendar(self) -> Optional[Dict[str, Any]]:
        """Parse calendar into fantasy-relevant format"""
        calendar = self.api.get_nfl_calendar_ondays()
        if not calendar:
            return None
        
        parsed_calendar = {
            'type': calendar.get('type'),
            'start_date': calendar.get('startDate'),
            'end_date': calendar.get('endDate'),
            'event_dates': []
        }
        
        if 'eventDate' in calendar and 'dates' in calendar['eventDate']:
            parsed_calendar['event_dates'] = calendar['eventDate']['dates']
        
        return parsed_calendar
    
    def get_fantasy_relevant_players(self, team_id: str) -> List[Dict[str, Any]]:
        """Get fantasy-relevant players from team roster"""
        roster = self.parse_team_roster(team_id)
        fantasy_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
        
        fantasy_players = []
        for player in roster:
            # Check if position is fantasy-relevant
            position = player['position']
            if position in fantasy_positions or any(pos in position.upper() for pos in fantasy_positions):
                fantasy_players.append(player)
        
        return fantasy_players
    
    def get_injured_players(self, team_id: str) -> List[Dict[str, Any]]:
        """Get injured players from team"""
        injuries = self.parse_team_injuries(team_id)
        injured_players = []
        
        for injury in injuries:
            if injury['status'] in ['Out', 'Questionable', 'Doubtful']:
                injured_players.append(injury)
        
        return injured_players
    
    def get_game_scores(self) -> List[Dict[str, Any]]:
        """Get current game scores"""
        games = self.parse_live_scores()
        scored_games = []
        
        for game in games:
            if game['teams'] and any(team['score'] is not None for team in game['teams']):
                scored_games.append(game)
        
        return scored_games

def main():
    """Demonstrate the structured parsers"""
    print("🏈 NFL Fantasy League JSON Parsers Demo")
    print("=" * 50)
    print("Parsing real NFL API data into structured format")
    print("for fantasy league integration")
    print()
    
    parsers = NFLFantasyParsers()
    
    # Parse live scores
    print("1. PARSING LIVE SCORES:")
    games = parsers.parse_live_scores()
    print(f"✅ Parsed {len(games)} games")
    if games:
        game = games[0]
        print(f"🎮 Sample game: {game['competition']} - {game['round']}")
        print(f"⏰ Status: {game['status']}")
        print(f"👥 Teams: {len(game['teams'])}")
        for team in game['teams']:
            print(f"   {team['name']}: {team['score']} {'(Winner)' if team['is_winner'] else ''}")
    
    # Parse player detail
    print("\n2. PARSING PLAYER DETAIL:")
    player = parsers.parse_player_detail("4360644")
    if player:
        print(f"✅ Player: {player['name']}")
        print(f"🔢 Jersey: #{player['jersey']}")
        print(f"📏 Height: {player['height']}")
        print(f"⚖️  Weight: {player['weight']}")
        print(f"🎓 College: {player.get('college', {}).get('name', 'Unknown')}")
        print(f"🏆 Experience: {player.get('experience_years', 'Unknown')} years")
        print(f"📊 Status: {player.get('status', {}).get('name', 'Unknown')}")
    
    # Parse team roster
    print("\n3. PARSING TEAM ROSTER:")
    roster = parsers.parse_team_roster("22")
    print(f"✅ Parsed {len(roster)} players")
    
    # Get fantasy-relevant players
    fantasy_players = parsers.get_fantasy_relevant_players("22")
    print(f"🏈 Fantasy-relevant players: {len(fantasy_players)}")
    
    # Group by position
    by_position = {}
    for player in fantasy_players:
        pos = player['position']
        if pos not in by_position:
            by_position[pos] = []
        by_position[pos].append(player)
    
    for pos, players in by_position.items():
        print(f"   {pos}: {len(players)} players")
    
    # Parse team injuries
    print("\n4. PARSING TEAM INJURIES:")
    injuries = parsers.parse_team_injuries("22")
    print(f"✅ Parsed {len(injuries)} injuries")
    
    # Get injured players
    injured_players = parsers.get_injured_players("22")
    print(f"🤕 Injured players: {len(injured_players)}")
    
    # Parse calendar
    print("\n5. PARSING CALENDAR:")
    calendar = parsers.parse_calendar()
    if calendar:
        print(f"✅ Calendar parsed")
        print(f"📅 Date range: {calendar['start_date']} to {calendar['end_date']}")
        print(f"📆 Event dates: {len(calendar['event_dates'])}")
    
    print("\n🏁 JSON PARSING DEMO COMPLETE!")
    print("=" * 50)
    print("💡 Key achievements:")
    print("✅ Structured parsing of all NFL API endpoints")
    print("✅ Fantasy-relevant data extraction")
    print("✅ Ready for database integration")
    print("✅ Clean, consistent data format")
    print("\n🚀 Ready to integrate into fantasy league system!")

if __name__ == "__main__":
    main()
