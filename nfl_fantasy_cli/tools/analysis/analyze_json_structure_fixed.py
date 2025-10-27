#!/usr/bin/env python3
"""
NFL API JSON Structure Analyzer - Fixed Version
Analyze the actual JSON responses and create structured parsers for fantasy league
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

class NFLJSONAnalyzer:
    """Analyze NFL API JSON responses and create structured parsers"""
    
    def __init__(self):
        self.api = nfl_api
    
    def analyze_live_scores_structure(self):
        """Analyze live scores JSON structure"""
        print("🏈 LIVE SCORES JSON STRUCTURE")
        print("=" * 40)
        
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
                
                # Show key game data
                print(f"\n📊 Key game data:")
                print(f"   id: {game.get('id')}")
                print(f"   competitionDisplayName: {game.get('competitionDisplayName')}")
                print(f"   roundName: {game.get('roundName')}")
                print(f"   startTime: {game.get('startTime')}")
                print(f"   statusText: {game.get('statusText')}")
                print(f"   gameTime: {game.get('gameTime')}")
                
                # Show competitor structure
                if 'homeCompetitor' in game:
                    home = game['homeCompetitor']
                    print(f"\n🏠 Home team structure:")
                    print(f"   Keys: {list(home.keys())}")
                    print(f"   name: {home.get('name')}")
                    print(f"   score: {home.get('score')}")
                    print(f"   isWinner: {home.get('isWinner')}")
                
                if 'awayCompetitor' in game:
                    away = game['awayCompetitor']
                    print(f"\n✈️  Away team structure:")
                    print(f"   Keys: {list(away.keys())}")
                    print(f"   name: {away.get('name')}")
                    print(f"   score: {away.get('score')}")
                    print(f"   isWinner: {away.get('isWinner')}")
        
        return live_data
    
    def analyze_player_detail_structure(self, player_id):
        """Analyze player detail JSON structure"""
        print(f"\n👤 PLAYER DETAIL JSON STRUCTURE - ID {player_id}")
        print("=" * 50)
        
        player_data = self.api.get_player_detail(player_id)
        if not player_data:
            print("❌ No player data")
            return None
        
        print(f"📊 Raw data size: {len(str(player_data))} characters")
        print(f"📋 Top-level keys: {list(player_data.keys())}")
        
        print(f"\n📊 Key player data:")
        print(f"   id: {player_data.get('id')}")
        print(f"   displayName: {player_data.get('displayName')}")
        print(f"   firstName: {player_data.get('firstName')}")
        print(f"   lastName: {player_data.get('lastName')}")
        print(f"   jersey: {player_data.get('jersey')}")
        print(f"   displayHeight: {player_data.get('displayHeight')}")
        print(f"   displayWeight: {player_data.get('displayWeight')}")
        print(f"   age: {player_data.get('age')}")
        print(f"   dateOfBirth: {player_data.get('dateOfBirth')}")
        print(f"   active: {player_data.get('active')}")
        
        # Show nested structures
        if 'birthPlace' in player_data:
            birth_place = player_data['birthPlace']
            print(f"\n🌍 Birth place structure:")
            print(f"   Keys: {list(birth_place.keys())}")
            print(f"   city: {birth_place.get('city')}")
            print(f"   state: {birth_place.get('state')}")
            print(f"   country: {birth_place.get('country')}")
        
        if 'experience' in player_data:
            experience = player_data['experience']
            print(f"\n🏆 Experience structure:")
            print(f"   Keys: {list(experience.keys())}")
            print(f"   years: {experience.get('years')}")
        
        if 'status' in player_data:
            status = player_data['status']
            print(f"\n📊 Status structure:")
            print(f"   Keys: {list(status.keys())}")
            print(f"   name: {status.get('name')}")
            print(f"   type: {status.get('type')}")
            print(f"   abbreviation: {status.get('abbreviation')}")
        
        return player_data
    
    def analyze_team_roster_structure(self, team_id):
        """Analyze team roster JSON structure"""
        print(f"\n👥 TEAM ROSTER JSON STRUCTURE - Team {team_id}")
        print("=" * 50)
        
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
                
                print(f"\n📊 Key athlete data:")
                print(f"   id: {athlete.get('id')}")
                print(f"   displayName: {athlete.get('displayName')}")
                print(f"   firstName: {athlete.get('firstName')}")
                print(f"   lastName: {athlete.get('lastName')}")
                print(f"   jersey: {athlete.get('jersey')}")
                print(f"   position: {athlete.get('position')}")
                print(f"   displayHeight: {athlete.get('displayHeight')}")
                print(f"   displayWeight: {athlete.get('displayWeight')}")
                print(f"   age: {athlete.get('age')}")
                print(f"   active: {athlete.get('active')}")
                
                # Show nested structures
                if 'college' in athlete:
                    college = athlete['college']
                    print(f"\n🎓 College structure:")
                    print(f"   Keys: {list(college.keys())}")
                    print(f"   name: {college.get('name')}")
                    print(f"   shortName: {college.get('shortName')}")
                    print(f"   abbrev: {college.get('abbrev')}")
                
                if 'position' in athlete:
                    position = athlete['position']
                    print(f"\n🏈 Position structure:")
                    print(f"   Type: {type(position)}")
                    if isinstance(position, dict):
                        print(f"   Keys: {list(position.keys())}")
                    else:
                        print(f"   Value: {position}")
                
                if 'teams' in athlete and athlete['teams']:
                    team = athlete['teams'][0]
                    print(f"\n🏟️  Team structure:")
                    print(f"   Keys: {list(team.keys())}")
                    print(f"   name: {team.get('name')}")
                    print(f"   shortName: {team.get('shortName')}")
        
        return roster_data
    
    def analyze_team_injuries_structure(self, team_id):
        """Analyze team injuries JSON structure"""
        print(f"\n🏥 TEAM INJURIES JSON STRUCTURE - Team {team_id}")
        print("=" * 50)
        
        injury_data = self.api.get_team_injuries(team_id)
        if not injury_data:
            print("❌ No injury data")
            return None
        
        print(f"📊 Raw data size: {len(str(injury_data))} characters")
        print(f"📋 Top-level keys: {list(injury_data.keys())}")
        
        print(f"\n📊 Pagination info:")
        print(f"   count: {injury_data.get('count')}")
        print(f"   pageIndex: {injury_data.get('pageIndex')}")
        print(f"   pageSize: {injury_data.get('pageSize')}")
        print(f"   pageCount: {injury_data.get('pageCount')}")
        
        if 'injuries' in injury_data:
            injuries = injury_data['injuries']
            print(f"🏥 Number of injuries: {len(injuries)}")
            
            if injuries:
                injury = injuries[0]
                print(f"\n📋 Injury structure:")
                print(f"   Keys: {list(injury.keys())}")
                
                print(f"\n📊 Key injury data:")
                print(f"   id: {injury.get('id')}")
                print(f"   status: {injury.get('status')}")
                print(f"   date: {injury.get('date')}")
                print(f"   longComment: {injury.get('longComment', '')[:100]}...")
                print(f"   shortComment: {injury.get('shortComment', '')[:100]}...")
                
                # Show nested structures
                if 'source' in injury:
                    source = injury['source']
                    print(f"\n📰 Source structure:")
                    print(f"   Keys: {list(source.keys())}")
                    print(f"   description: {source.get('description')}")
                    print(f"   state: {source.get('state')}")
                
                if 'type' in injury:
                    injury_type = injury['type']
                    print(f"\n🤕 Injury type structure:")
                    print(f"   Keys: {list(injury_type.keys())}")
                    print(f"   name: {injury_type.get('name')}")
                    print(f"   description: {injury_type.get('description')}")
                    print(f"   abbreviation: {injury_type.get('abbreviation')}")
        
        return injury_data
    
    def analyze_player_statistics_structure(self, player_id, year=2023):
        """Analyze player statistics JSON structure"""
        print(f"\n📊 PLAYER STATISTICS JSON STRUCTURE - ID {player_id}, Year {year}")
        print("=" * 60)
        
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
                    
                    print(f"\n📊 Key split data:")
                    print(f"   id: {split.get('id')}")
                    print(f"   name: {split.get('name')}")
                    print(f"   displayName: {split.get('displayName')}")
                    print(f"   abbreviation: {split.get('abbreviation')}")
                    print(f"   type: {split.get('type')}")
                    
                    # Show categories structure
                    if 'categories' in split and split['categories']:
                        categories = split['categories']
                        print(f"\n📊 Categories structure:")
                        print(f"   Number of categories: {len(categories)}")
                        
                        if categories:
                            category = categories[0]
                            print(f"   Sample category keys: {list(category.keys())}")
                            print(f"   name: {category.get('name')}")
                            print(f"   displayName: {category.get('displayName')}")
                            
                            if 'stats' in category and category['stats']:
                                stats_list = category['stats']
                                print(f"   Number of stats: {len(stats_list)}")
                                
                                if stats_list:
                                    stat = stats_list[0]
                                    print(f"   Sample stat keys: {list(stat.keys())}")
                                    print(f"   name: {stat.get('name')}")
                                    print(f"   displayName: {stat.get('displayName')}")
                                    print(f"   value: {stat.get('value')}")
        
        return stats_data
    
    def analyze_calendar_structure(self):
        """Analyze calendar JSON structure"""
        print(f"\n📅 CALENDAR JSON STRUCTURE")
        print("=" * 30)
        
        calendar = self.api.get_nfl_calendar_ondays()
        if not calendar:
            print("❌ No calendar data")
            return None
        
        print(f"📊 Raw data size: {len(str(calendar))} characters")
        print(f"📋 Top-level keys: {list(calendar.keys())}")
        
        print(f"\n📊 Key calendar data:")
        print(f"   type: {calendar.get('type')}")
        print(f"   startDate: {calendar.get('startDate')}")
        print(f"   endDate: {calendar.get('endDate')}")
        
        if 'eventDate' in calendar:
            event_date = calendar['eventDate']
            print(f"\n📅 Event date structure:")
            print(f"   Keys: {list(event_date.keys())}")
            print(f"   type: {event_date.get('type')}")
            
            if 'dates' in event_date:
                dates = event_date['dates']
                print(f"   Number of dates: {len(dates)}")
                if dates:
                    print(f"   First date: {dates[0]}")
                    print(f"   Last date: {dates[-1]}")
        
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
