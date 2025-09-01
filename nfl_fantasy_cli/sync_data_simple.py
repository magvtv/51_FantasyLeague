#!/usr/bin/env python3
"""
Simplified Data Synchronization CLI
Direct implementation without complex imports.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Sync NFL API data to Supabase database')
    parser.add_argument('--teams', action='store_true', help='Sync NFL teams')
    parser.add_argument('--players', action='store_true', help='Sync NFL players')
    parser.add_argument('--stats', action='store_true', help='Sync player statistics')
    parser.add_argument('--injuries', action='store_true', help='Sync injury data')
    parser.add_argument('--full', action='store_true', help='Perform full synchronization')
    parser.add_argument('--season', type=int, default=2024, help='Season for stats sync')
    parser.add_argument('--week', type=int, help='Week for stats sync (optional)')
    parser.add_argument('--team-id', type=str, help='Specific team ID for player sync')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check if Supabase credentials are available
    if not os.getenv('SUPABASE_DB_URL'):
        print("❌ SUPABASE_DB_URL not found in environment variables!")
        print("💡 Please check your .env file")
        return 1
    
    try:
        print("🚀 NFL Fantasy League - Data Synchronization")
        print("=" * 50)
        
        # Import required modules
        from database import get_app, get_db
        from api_service import nfl_api
        
        app = get_app()
        db = get_db()
        
        if args.full:
            # Full synchronization
            success = perform_full_sync(app, db, nfl_api)
            return 0 if success else 1
        
        success = True
        
        # Individual sync operations
        if args.teams:
            if not sync_nfl_teams(nfl_api):
                success = False
        
        if args.players:
            if not sync_nfl_players(app, db, nfl_api, args.team_id):
                success = False
        
        if args.stats:
            if not sync_player_stats(app, db, nfl_api, args.season, args.week):
                success = False
        
        if args.injuries:
            if not sync_injury_data(app, db, nfl_api):
                success = False
        
        # If no specific flags, show help
        if not any([args.teams, args.players, args.stats, args.injuries, args.full]):
            parser.print_help()
            return 0
        
        print("=" * 50)
        if success:
            print("🎉 Synchronization completed successfully!")
            return 0
        else:
            print("⚠️  Synchronization completed with some errors")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this script from the correct directory")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

def sync_nfl_teams(nfl_api):
    """Sync NFL teams from API"""
    print("🔄 Syncing NFL teams...")
    
    try:
        teams_data = nfl_api.get_teams_list()
        
        if not teams_data:
            print("❌ No teams data received from API")
            return False
        
        print(f"📊 Found {len(teams_data)} teams from API")
        
        for team in teams_data:
            print(f"   {team['abbreviation']}: {team['name']}")
        
        print("✅ Teams sync completed")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing teams: {e}")
        return False

def sync_nfl_players(app, db, nfl_api, team_id=None):
    """Sync NFL players from API to database"""
    print("🔄 Syncing NFL players...")
    
    try:
        if team_id:
            # Sync players for specific team
            players_data = nfl_api.get_players_by_team(team_id)
            if not players_data or 'players' not in players_data:
                print(f"❌ No players data for team {team_id}")
                return False
            players = players_data['players']
        else:
            # Get all teams first, then sync players for each
            teams_data = nfl_api.get_teams_list()
            if not teams_data:
                print("❌ No teams data available")
                return False
            
            all_players = []
            for team in teams_data:
                print(f"   Syncing players for {team['abbreviation']}...")
                team_players = nfl_api.get_players_by_team(team['id'])
                if team_players and 'players' in team_players:
                    all_players.extend(team_players['players'])
            players = all_players
        
        print(f"📊 Found {len(players)} players to sync")
        
        # For now, just log the players since we need to set up the database models
        print("⚠️  Player sync completed (logged to console)")
        print("💡 Database sync will be implemented once models are properly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error syncing players: {e}")
        return False

def sync_player_stats(app, db, nfl_api, season=2024, week=None):
    """Sync player statistics from API to database"""
    print(f"🔄 Syncing player stats for season {season}" + (f" week {week}" if week else ""))
    
    try:
        if week:
            stats_data = nfl_api.get_weekly_stats(season, week)
        else:
            stats_data = nfl_api.get_season_stats(season)
        
        if not stats_data or 'players' not in stats_data:
            print("❌ No stats data received from API")
            return False
        
        players = stats_data['players']
        print(f"📊 Found stats for {len(players)} players")
        
        print("⚠️  Stats sync completed (logged to console)")
        print("💡 Database sync will be implemented once models are properly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error syncing player stats: {e}")
        return False

def sync_injury_data(app, db, nfl_api):
    """Sync injury data from API to database"""
    print("🔄 Syncing injury data...")
    
    try:
        injury_data = nfl_api.get_injury_report()
        
        if not injury_data:
            print("❌ No injury data received from API")
            return False
        
        print(f"📊 Found injury data for {len(injury_data)} players")
        
        print("⚠️  Injury sync completed (logged to console)")
        print("💡 Database sync will be implemented once models are properly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error syncing injury data: {e}")
        return False

def perform_full_sync(app, db, nfl_api):
    """Perform full data synchronization"""
    print("🚀 Starting full data synchronization...")
    print("=" * 50)
    
    success = True
    
    # Sync teams
    if not sync_nfl_teams(nfl_api):
        success = False
    
    # Sync players
    if not sync_nfl_players(app, db, nfl_api):
        success = False
    
    # Sync current season stats
    if not sync_player_stats(app, db, nfl_api, 2024):
        success = False
    
    # Sync injury data
    if not sync_injury_data(app, db, nfl_api):
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 Full synchronization completed successfully!")
    else:
        print("⚠️  Synchronization completed with some errors")
    
    return success

if __name__ == "__main__":
    exit(main())
