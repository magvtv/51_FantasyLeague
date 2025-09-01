#!/usr/bin/env python3
"""
NFL Data Import Script
Fetches player data from RapidAPI and imports to PostgreSQL database
"""

import requests
import psycopg2
import json
import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables
load_dotenv(dotenv_path='../.env')  # Look for .env in parent directory
if not os.path.exists('../.env'):
    load_dotenv()  # Fallback to current directory

# API Configuration
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST", "nfl-api-data.p.rapidapi.com")
BASE_URL = f"https://{API_HOST}"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'nfl_fantasy'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

class NFLDataImporter:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ Connected to PostgreSQL database")
        except psycopg2.Error as e:
            print(f"❌ Error connecting to database: {e}")
            sys.exit(1)
    
    def close_db(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("📝 Database connection closed")
    
    def fetch_teams(self) -> Optional[List[Dict]]:
        """Fetch NFL teams from API"""
        try:
            print("🏈 Fetching NFL teams...")
            response = requests.get(f"{BASE_URL}/nfl-team-listing/v1/data", headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Fetched {len(data.get('teams', []))} teams")
            return data.get('teams', [])
        except requests.RequestException as e:
            print(f"❌ Error fetching teams: {e}")
            return None
    
    def fetch_players_by_team(self, team_id: str) -> Optional[List[Dict]]:
        """Fetch players for a specific team"""
        try:
            print(f"👥 Fetching players for team {team_id}...")
            response = requests.get(f"{BASE_URL}/players", headers=HEADERS, params={"team": team_id})
            response.raise_for_status()
            data = response.json()
            return data.get('players', [])
        except requests.RequestException as e:
            print(f"❌ Error fetching players for team {team_id}: {e}")
            return None
    
    def calculate_fantasy_price(self, player: Dict) -> float:
        """Calculate fantasy price based on player stats and position"""
        position = player.get('position', 'UNKNOWN')
        
        # Base prices by position (in dollars)
        base_prices = {
            'QB': 8000000,   # $8M
            'RB': 7000000,   # $7M
            'WR': 6500000,   # $6.5M
            'TE': 5000000,   # $5M
            'K': 4000000,    # $4M
            'DEF': 4500000,  # $4.5M
        }
        
        base_price = base_prices.get(position, 5000000)
        
        # Adjust based on available stats (simplified pricing model)
        # In a real system, you'd use historical performance data
        multiplier = 1.0
        
        # You can enhance this with actual performance metrics
        if player.get('fantasy_points_last_season', 0) > 200:
            multiplier = 1.5
        elif player.get('fantasy_points_last_season', 0) > 150:
            multiplier = 1.2
        elif player.get('fantasy_points_last_season', 0) < 50:
            multiplier = 0.8
        
        return int(base_price * multiplier)
    
    def import_players(self, players: List[Dict], team_abbr: str) -> int:
        """Import players to database"""
        if not players:
            return 0
        
        imported_count = 0
        
        for player in players:
            try:
                # Extract player data
                nfl_id = player.get('id', f"{team_abbr}_{player.get('name', 'unknown')}")
                name = player.get('name', 'Unknown Player')
                position = player.get('position', 'UNKNOWN')
                price = self.calculate_fantasy_price(player)
                total_points = player.get('fantasy_points_season', 0.0)
                
                # Insert or update player
                insert_query = """
                    INSERT INTO nfl_players (nfl_id, name, position, team, price, total_points, is_injured)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (nfl_id) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        position = EXCLUDED.position,
                        team = EXCLUDED.team,
                        price = EXCLUDED.price,
                        total_points = EXCLUDED.total_points,
                        is_injured = EXCLUDED.is_injured
                """
                
                self.cursor.execute(insert_query, (
                    nfl_id, name, position, team_abbr, price, total_points, False
                ))
                
                imported_count += 1
                
            except Exception as e:
                print(f"⚠️  Error importing player {player.get('name', 'Unknown')}: {e}")
                continue
        
        self.conn.commit()
        return imported_count
    
    def import_sample_weekly_scores(self):
        """Import sample weekly scores for testing"""
        print("📊 Importing sample weekly scores...")
        
        # Get all players
        self.cursor.execute("SELECT id, position FROM nfl_players LIMIT 50")
        players = self.cursor.fetchall()
        
        import random
        
        for week in range(1, 6):  # Sample data for weeks 1-5
            for player_id, position in players:
                # Generate realistic stats based on position
                stats = self.generate_sample_stats(position)
                fantasy_points = self.calculate_fantasy_points(stats)
                
                insert_query = """
                    INSERT INTO weekly_scores (
                        player_id, week, season, passing_yards, passing_tds, 
                        passing_interceptions, rushing_yards, rushing_tds,
                        receiving_yards, receiving_tds, receptions, fumbles,
                        field_goals_made, extra_points_made, def_touchdowns,
                        def_interceptions, def_points_allowed, fantasy_points
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id, week, season) DO NOTHING
                """
                
                self.cursor.execute(insert_query, (
                    player_id, week, 2024,
                    stats['passing_yards'], stats['passing_tds'], stats['passing_interceptions'],
                    stats['rushing_yards'], stats['rushing_tds'],
                    stats['receiving_yards'], stats['receiving_tds'], stats['receptions'],
                    stats['fumbles'], stats['field_goals_made'], stats['extra_points_made'],
                    stats['def_touchdowns'], stats['def_interceptions'], 
                    stats['def_points_allowed'], fantasy_points
                ))
        
        self.conn.commit()
        print(f"✅ Sample weekly scores imported for {len(players)} players")
    
    def generate_sample_stats(self, position: str) -> Dict:
        """Generate realistic sample stats based on position"""
        import random
        
        stats = {
            'passing_yards': 0, 'passing_tds': 0, 'passing_interceptions': 0,
            'rushing_yards': 0, 'rushing_tds': 0,
            'receiving_yards': 0, 'receiving_tds': 0, 'receptions': 0,
            'fumbles': 0, 'field_goals_made': 0, 'extra_points_made': 0,
            'def_touchdowns': 0, 'def_interceptions': 0, 'def_points_allowed': 0
        }
        
        if position == 'QB':
            stats['passing_yards'] = random.randint(180, 350)
            stats['passing_tds'] = random.randint(0, 4)
            stats['passing_interceptions'] = random.randint(0, 2)
            stats['rushing_yards'] = random.randint(0, 50)
            stats['rushing_tds'] = random.randint(0, 1)
        elif position == 'RB':
            stats['rushing_yards'] = random.randint(40, 150)
            stats['rushing_tds'] = random.randint(0, 2)
            stats['receiving_yards'] = random.randint(10, 60)
            stats['receiving_tds'] = random.randint(0, 1)
            stats['receptions'] = random.randint(2, 8)
        elif position == 'WR':
            stats['receiving_yards'] = random.randint(30, 120)
            stats['receiving_tds'] = random.randint(0, 2)
            stats['receptions'] = random.randint(3, 10)
        elif position == 'TE':
            stats['receiving_yards'] = random.randint(20, 80)
            stats['receiving_tds'] = random.randint(0, 1)
            stats['receptions'] = random.randint(2, 7)
        elif position == 'K':
            stats['field_goals_made'] = random.randint(0, 4)
            stats['extra_points_made'] = random.randint(0, 5)
        elif position == 'DEF':
            stats['def_touchdowns'] = random.randint(0, 1)
            stats['def_interceptions'] = random.randint(0, 3)
            stats['def_points_allowed'] = random.randint(7, 35)
        
        # Random fumbles for skill positions
        if position in ['QB', 'RB', 'WR', 'TE']:
            stats['fumbles'] = random.randint(0, 1) if random.random() < 0.1 else 0
        
        return stats
    
    def calculate_fantasy_points(self, stats: Dict) -> float:
        """Calculate fantasy points from stats (PPR scoring)"""
        points = 0.0
        
        # Passing
        points += (stats['passing_yards'] / 25) * 1
        points += stats['passing_tds'] * 4
        points -= stats['passing_interceptions'] * 2
        
        # Rushing
        points += (stats['rushing_yards'] / 10) * 1
        points += stats['rushing_tds'] * 6
        
        # Receiving
        points += (stats['receiving_yards'] / 10) * 1
        points += stats['receiving_tds'] * 6
        points += stats['receptions'] * 1  # PPR
        
        # Fumbles
        points -= stats['fumbles'] * 2
        
        # Kicking
        points += stats['field_goals_made'] * 3
        points += stats['extra_points_made'] * 1
        
        # Defense
        points += stats['def_touchdowns'] * 6
        points += stats['def_interceptions'] * 2
        
        # Points allowed by defense
        points_allowed = stats['def_points_allowed']
        if points_allowed == 0:
            points += 10
        elif points_allowed <= 6:
            points += 7
        elif points_allowed <= 13:
            points += 4
        elif points_allowed <= 20:
            points += 1
        elif points_allowed <= 27:
            points += 0
        else:
            points -= 1
        
        return round(points, 2)
    
    def run_import(self):
        """Main import process"""
        if not API_KEY:
            print("❌ RAPIDAPI_KEY not found in environment variables")
            print("Please set your RapidAPI key in .env file")
            return
        
        print("🏈 Starting NFL data import...")
        
        self.connect_db()
        
        try:
            # Fetch teams
            teams = self.fetch_teams()
            if not teams:
                print("❌ No teams data available")
                return
            
            total_players = 0
            
            # Process each team
            for team in teams[:5]:  # Limit to first 5 teams for testing
                team_abbr = team.get('abbreviation', team.get('name', 'UNK'))
                team_id = team.get('id', team_abbr)
                
                print(f"\n🏈 Processing {team.get('name', 'Unknown Team')} ({team_abbr})")
                
                # Fetch players for this team
                players = self.fetch_players_by_team(team_id)
                if players:
                    count = self.import_players(players, team_abbr)
                    total_players += count
                    print(f"✅ Imported {count} players for {team_abbr}")
            
            print(f"\n📊 Import Summary:")
            print(f"Total players imported: {total_players}")
            
            # Import sample weekly scores
            self.import_sample_weekly_scores()
            
            print("✅ NFL data import completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during import: {e}")
            self.conn.rollback()
        
        finally:
            self.close_db()

def main():
    """Main function"""
    print("🏈 NFL Fantasy Data Importer")
    print("=" * 50)
    
    importer = NFLDataImporter()
    importer.run_import()

if __name__ == "__main__":
    main()
