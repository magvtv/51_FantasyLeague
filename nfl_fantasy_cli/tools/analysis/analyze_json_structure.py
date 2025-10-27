#!/usr/bin/env python3
"""
NFL API JSON Structure Analyzer
Analyze the actual JSON responses and create structured parsers for fantasy league
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

class NFLJSONAnalyzer:
    """Analyze NFL API JSON responses and create structured parsers"""
    
    def __init__(self):
        self.api = nfl_api
    
    def analyze_live_scores_structure(self):
        """Analyze live scores JSON structure"""
        print("🏈 ANALYZING LIVE SCORES JSON STRUCTURE")
        print("=" * 50)
        
        live_data = self.api.get_live_scores()
        if not live_data:
            print("❌ No live scores data")
            return None
        
        print(f"📊 Raw data size: {len(str(live_data))} characters")
        print(f"📋 Top-level keys: {list(live_data.keys())}")
        
        if 'live' in live_data:
            games = live_data['live']
            print(f"🎮 Number of games: {len(games)}")
            
            if games:
                game = games[0]
                print(f"\n📋 Game structure:")
                print(f"   Keys: {list(game.keys())}")
                
                # Show sample game data
                print(f"\n📊 Sample game data:")
                for key, value in game.items():
                    if isinstance(value, (str, int, float, bool)):
                        print(f"   {key}: {value}")
                    elif isinstance(value, dict):
                        print(f"   {key}: {type(value)} with keys {list(value.keys())}")
                    elif isinstance(value, list):
                        print(f"   {key}: {type(value)} with {len(value)} items")
                    else:
                        print(f"   {key}: {type(value)}")
        
        return live_data
    
    def analyze_player_detail_structure(self, player_id):
        """Analyze player detail JSON structure"""
        print(f"\n👤 ANALYZING PLAYER DETAIL JSON STRUCTURE - ID {player_id}")
        print("=" * 60)
        
        player_data = self.api.get_player_detail(player_id)
        if not player_data:
            print("❌ No player data")
            return None
        
        print(f"📊 Raw data size: {len(str(player_data))} characters")
        print(f"📋 Top-level keys: {list(player_data.keys())}")
        
        print(f"\n📊 Player data structure:")
        for key, value in player_data.items():
            if isinstance(value, (str, int, float, bool)):
                print(f"   {key}: {value}")
            elif isinstance(value, dict):
                print(f"   {key}: {type(value)} with keys {list(value.keys())}")
                # Show nested structure for important fields
                if key in ['position', 'team', 'college']:
                    for nested_key, nested_value in value.items():
                        print(f"     {nested_key}: {nested_value}")
            elif isinstance(value, list):
                print(f"   {key}: {type(value)} with {len(value)} items")
            else:
                print(f"   {key}: {type(value)}")
        
        return player_data
    
    def analyze_team_roster_structure(self, team_id):
        """Analyze team roster JSON structure"""
        print(f"\n👥 ANALYZING TEAM ROSTER JSON STRUCTURE - Team {team_id}")
        print("=" * 60)
        
        roster_data = self.api.get_team_players(team_id)
        if not roster_data:
            print("❌ No roster data")
            return None
        
        print(f"📊 Raw data size: {len(str(roster_data))} characters")
        print(f"📋 Top-level keys: {list(roster_data.keys())}")
        
        if 'athletes' in roster_data:
            athletes = roster_data['athletes']
            print(f"👥 Number of athletes: {len(athletes)}")
            
            if athletes:
                athlete = athletes[0]
                print(f"\n📋 Athlete structure:")
                print(f"   Keys: {list(athlete.keys())}")
                
                print(f"\n📊 Sample athlete data:")
                for key, value in athlete.items():
                    if isinstance(value, (str, int, float, bool)):
                        print(f"   {key}: {value}")
                    elif isinstance(value, dict):
                        print(f"   {key}: {type(value)} with keys {list(value.keys())}")
                        # Show nested structure for important fields
                        if key in ['position', 'college']:
                            for nested_key, nested_value in value.items():
                                print(f"     {nested_key}: {nested_value}")
                    elif isinstance(value, list):
                        print(f"   {key}: {type(value)} with {len(value)} items")
                    else:
                        print(f"   {key}: {type(value)}")
        
        return roster_data
    
    def analyze_team_injuries_structure(self, team_id):
        """Analyze team injuries JSON structure"""
        print(f"\n🏥 ANALYZING TEAM INJURIES JSON STRUCTURE - Team {team_id}")
        print("=" * 60)
        
        injury_data = self.api.get_team_injuries(team_id)
        if not injury_data:
            print("❌ No injury data")
            return None
        
        print(f"📊 Raw data size: {len(str(injury_data))} characters")
        print(f"📋 Top-level keys: {list(injury_data.keys())}")
        
        if 'injuries' in injury_data:
            injuries = injury_data['injuries']
            print(f"🏥 Number of injuries: {len(injuries)}")
            
            if injuries:
                injury = injuries[0]
                print(f"\n📋 Injury structure:")
                print(f"   Keys: {list(injury.keys())}")
                
                print(f"\n📊 Sample injury data:")
                for key, value in injury.items():
                    if isinstance(value, (str, int, float, bool)):
                        print(f"   {key}: {value}")
                    elif isinstance(value, dict):
                        print(f"   {key}: {type(value)} with keys {list(value.keys())}")
                    elif isinstance(value, list):
                        print(f"   {key}: {type(value)} with {len(value)} items")
                    else:
                        print(f"   {key}: {type(value)}")
        
        return injury_data
    
    def analyze_player_statistics_structure(self, player_id, year=2023):
        """Analyze player statistics JSON structure"""
        print(f"\n📊 ANALYZING PLAYER STATISTICS JSON STRUCTURE - ID {player_id}, Year {year}")
        print("=" * 70)
        
        stats_data = self.api.get_player_statistics(player_id, year)
        if not stats_data:
            print("❌ No statistics data")
            return None
        
        print(f"📊 Raw data size: {len(str(stats_data))} characters")
        print(f"📋 Top-level keys: {list(stats_data.keys())}")
        
        if 'statistics' in stats_data:
            stats = stats_data['statistics']
            print(f"\n📋 Statistics structure:")
            print(f"   Keys: {list(stats.keys())}")
            
            if 'splits' in stats and stats['splits']:
                splits = stats['splits']
                print(f"📈 Number of splits: {len(splits)}")
                
                if splits:
                    split = splits[0]
                    print(f"\n📋 Split structure:")
                    print(f"   Keys: {list(split.keys())}")
                    
                    print(f"\n📊 Sample split data:")
                    for key, value in split.items():
                        if isinstance(value, (str, int, float, bool)):
                            print(f"   {key}: {value}")
                        elif isinstance(value, dict):
                            print(f"   {key}: {type(value)} with keys {list(value.keys())}")
                        elif isinstance(value, list):
                            print(f"   {key}: {type(value)} with {len(value)} items")
                            # Show categories structure
                            if key == 'categories' and value:
                                category = value[0]
                                print(f"     Sample category: {list(category.keys())}")
                                if 'stats' in category:
                                    print(f"       Stats: {len(category['stats'])} items")
                        else:
                            print(f"   {key}: {type(value)}")
        
        return stats_data
    
    def analyze_calendar_structure(self):
        """Analyze calendar JSON structure"""
        print(f"\n📅 ANALYZING CALENDAR JSON STRUCTURE")
        print("=" * 40)
        
        calendar = self.api.get_nfl_calendar_ondays()
        if not calendar:
            print("❌ No calendar data")
            return None
        
        print(f"📊 Raw data size: {len(str(calendar))} characters")
        print(f"📋 Top-level keys: {list(calendar.keys())}")
        
        print(f"\n📊 Calendar structure:")
        for key, value in calendar.items():
            if isinstance(value, (str, int, float, bool)):
                print(f"   {key}: {value}")
            elif isinstance(value, dict):
                print(f"   {key}: {type(value)} with keys {list(value.keys())}")
                # Show eventDate structure
                if key == 'eventDate':
                    for nested_key, nested_value in value.items():
                        if isinstance(nested_value, list):
                            print(f"     {nested_key}: {type(nested_value)} with {len(nested_value)} items")
                        else:
                            print(f"     {nested_key}: {nested_value}")
            elif isinstance(value, list):
                print(f"   {key}: {type(value)} with {len(value)} items")
            else:
                print(f"   {key}: {type(value)}")
        
        return calendar
    
    def save_sample_data(self):
        """Save sample JSON data for analysis"""
        print(f"\n💾 SAVING SAMPLE JSON DATA")
        print("=" * 30)
        
        sample_data = {}
        
        # Live scores
        live_data = self.api.get_live_scores()
        if live_data:
            sample_data['live_scores'] = live_data
        
        # Player detail
        player_data = self.api.get_player_detail("4360644")
        if player_data:
            sample_data['player_detail'] = player_data
        
        # Team roster
        roster_data = self.api.get_team_players("22")
        if roster_data:
            sample_data['team_roster'] = roster_data
        
        # Team injuries
        injury_data = self.api.get_team_injuries("22")
        if injury_data:
            sample_data['team_injuries'] = injury_data
        
        # Player statistics
        stats_data = self.api.get_player_statistics("15035", 2023)
        if stats_data:
            sample_data['player_statistics'] = stats_data
        
        # Calendar
        calendar = self.api.get_nfl_calendar_ondays()
        if calendar:
            sample_data['calendar'] = calendar
        
        # Save to file
        with open('nfl_api_sample_data.json', 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"✅ Saved sample data to nfl_api_sample_data.json")
        print(f"📊 Total size: {len(str(sample_data))} characters")
        
        return sample_data

def main():
    """Main analysis function"""
    print("🔍 NFL API JSON STRUCTURE ANALYSIS")
    print("=" * 50)
    print("Analyzing actual JSON responses to understand data structure")
    print("for fantasy league integration")
    print()
    
    analyzer = NFLJSONAnalyzer()
    
    # Analyze all structures
    analyzer.analyze_live_scores_structure()
    analyzer.analyze_player_detail_structure("4360644")
    analyzer.analyze_team_roster_structure("22")
    analyzer.analyze_team_injuries_structure("22")
    analyzer.analyze_player_statistics_structure("15035", 2023)
    analyzer.analyze_calendar_structure()
    
    # Save sample data
    sample_data = analyzer.save_sample_data()
    
    print("\n🏁 JSON STRUCTURE ANALYSIS COMPLETE!")
    print("=" * 50)
    print("📋 Next steps:")
    print("1. Review the JSON structures above")
    print("2. Check nfl_api_sample_data.json for full data")
    print("3. Create structured parsers for fantasy league")
    print("4. Map API data to your database schema")

if __name__ == "__main__":
    main()
