#!/usr/bin/env python3
"""
Data Synchronization CLI
Command-line interface for syncing NFL API data to Supabase database.
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
        # Import the data sync service
        from data_sync_service import data_sync
        
        print("🚀 NFL Fantasy League - Data Synchronization")
        print("=" * 50)
        
        if args.full:
            # Full synchronization
            success = data_sync.full_sync()
            return 0 if success else 1
        
        success = True
        
        # Individual sync operations
        if args.teams:
            if not data_sync.sync_nfl_teams():
                success = False
        
        if args.players:
            if not data_sync.sync_nfl_players(args.team_id):
                success = False
        
        if args.stats:
            if not data_sync.sync_player_stats(args.season, args.week):
                success = False
        
        if args.injuries:
            if not data_sync.sync_injury_data():
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

if __name__ == "__main__":
    exit(main())
