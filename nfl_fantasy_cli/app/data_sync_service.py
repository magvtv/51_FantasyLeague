#!/usr/bin/env python3
"""
Data Synchronization Service
Syncs external NFL API data into Supabase database for fantasy league use.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Add the current directory to the path for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from api_service import nfl_api
from database import get_db, get_app
from models import NFLPlayer, User, FantasyTeam, TeamPlayer, WeeklyScore

load_dotenv()

class DataSyncService:
    """Service to sync NFL API data with Supabase database"""
    
    def __init__(self):
        self.app = get_app()
        self.db = get_db()
        self.nfl_api = nfl_api
        
    def sync_nfl_teams(self):
        """Sync NFL teams from API to database"""
        print("🔄 Syncing NFL teams...")
        
        try:
            # Get teams from NFL API
            teams_data = self.nfl_api.get_teams_list()
            
            if not teams_data:
                print("No teams data received from API")
                return False
            
            print(f"Found {len(teams_data)} teams from API")
            
            # For now, we'll just log the teams since we don't have a teams table
            # You can add a teams table later if needed
            for team in teams_data:
                print(f"   {team['abbreviation']}: {team['name']}")
            
            print("Teams sync completed (logged to console)")
            return True
            
        except Exception as e:
            print(f"Error syncing teams: {e}")
            return False
    
    def sync_nfl_players(self, team_id: Optional[str] = None):
        """Sync NFL players from API to database"""
        print("Syncing NFL players...")
        
        try:
            if team_id:
                # Sync players for specific team
                players_data = self.nfl_api.get_players_by_team(team_id)
                if not players_data or 'players' not in players_data:
                    print(f"No players data for team {team_id}")
                    return False
                players = players_data['players']
            else:
                # Get all teams first, then sync players for each
                teams_data = self.nfl_api.get_teams_list()
                if not teams_data:
                    print("No teams data available")
                    return False
                
                all_players = []
                for team in teams_data:
                    print(f"   Syncing players for {team['abbreviation']}...")
                    team_players = self.nfl_api.get_players_by_team(team['id'])
                    if team_players and 'players' in team_players:
                        all_players.extend(team_players['players'])
                players = all_players
            
            print(f"Found {len(players)} players to sync")
            
            # Sync players to database
            synced_count = 0
            with self.app.app_context():
                for player_data in players:
                    if self._sync_player_to_db(player_data):
                        synced_count += 1
                
                self.db.session.commit()
            
            print(f"Successfully synced {synced_count}/{len(players)} players")
            return True
            
        except Exception as e:
            print(f"Error syncing players: {e}")
            return False
    
    def _sync_player_to_db(self, player_data: Dict[str, Any]) -> bool:
        """Sync individual player to database"""
        try:
            # Check if player already exists
            existing_player = NFLPlayer.query.filter_by(nfl_id=str(player_data.get('id'))).first()
            
            if existing_player:
                # Update existing player
                existing_player.name = player_data.get('name', 'Unknown')
                existing_player.position = player_data.get('position', 'UNKNOWN')
                existing_player.team = self._get_team_abbreviation(player_data.get('team_id'))
                print(f"   Updated: {existing_player.name} ({existing_player.position})")
            else:
                # Create new player
                new_player = NFLPlayer(
                    nfl_id=str(player_data.get('id')),
                    name=player_data.get('name', 'Unknown'),
                    position=player_data.get('position', 'UNKNOWN'),
                    team=self._get_team_abbreviation(player_data.get('team_id')),
                    price=5000000,  # Default price
                    total_points=0.0
                )
                self.db.session.add(new_player)
                print(f"   Added: {new_player.name} ({new_player.position})")
            
            return True
            
        except Exception as e:
            print(f"   Error syncing player {player_data.get('name', 'Unknown')}: {e}")
            return False
    
    def _get_team_abbreviation(self, team_id: str) -> str:
        """Get team abbreviation from team ID"""
        # This is a simple mapping - you might want to create a proper teams table
        team_mapping = {
            '1': 'ARI', '2': 'ATL', '3': 'BAL', '4': 'BUF', '5': 'CAR',
            '6': 'CHI', '7': 'CIN', '8': 'CLE', '9': 'DAL', '10': 'DEN',
            '11': 'DET', '12': 'GB', '13': 'HOU', '14': 'IND', '15': 'JAX',
            '16': 'KC', '17': 'LV', '18': 'LAC', '19': 'LAR', '20': 'MIA',
            '21': 'MIN', '22': 'NE', '23': 'NO', '24': 'NYG', '25': 'NYJ',
            '26': 'PHI', '27': 'PIT', '28': 'SEA', '29': 'SF', '30': 'TB',
            '31': 'TEN', '32': 'WAS'
        }
        return team_mapping.get(str(team_id), 'UNK')
    
    def sync_player_stats(self, season: int = 2024, week: Optional[int] = None):
        """Sync player statistics from API to database"""
        print(f"Syncing player stats for season {season}" + (f" week {week}" if week else ""))
        
        try:
            if week:
                stats_data = self.nfl_api.get_weekly_stats(season, week)
            else:
                stats_data = self.nfl_api.get_season_stats(season)
            
            if not stats_data or 'players' not in stats_data:
                print("No stats data received from API")
                return False
            
            players = stats_data['players']
            print(f"Found stats for {len(players)} players")
            
            # Sync stats to database
            synced_count = 0
            with self.app.app_context():
                for player_stats in players:
                    if self._sync_player_stats_to_db(player_stats, season, week):
                        synced_count += 1
                
                self.db.session.commit()
            
            print(f"Successfully synced stats for {synced_count}/{len(players)} players")
            return True
            
        except Exception as e:
            print(f"Error syncing player stats: {e}")
            return False
    
    def _sync_player_stats_to_db(self, player_stats: Dict[str, Any], season: int, week: Optional[int] = None) -> bool:
        """Sync individual player stats to database"""
        try:
            player_id = player_stats.get('playerId') or player_stats.get('id')
            if not player_id:
                return False
            
            # Find player in database
            player = NFLPlayer.query.filter_by(nfl_id=str(player_id)).first()
            if not player:
                print(f"   Player {player_id} not found in database, skipping stats")
                return False
            
            # Check if weekly score already exists
            existing_score = WeeklyScore.query.filter_by(
                player_id=player.id,
                week=week or 0,
                season=season
            ).first()
            
            if existing_score:
                # Update existing score
                self._update_weekly_score(existing_score, player_stats)
                print(f"   Updated stats: {player.name} week {week or 'season'}")
            else:
                # Create new weekly score
                new_score = WeeklyScore(
                    player_id=player.id,
                    week=week or 0,
                    season=season
                )
                self._update_weekly_score(new_score, player_stats)
                self.db.session.add(new_score)
                print(f"   Added stats: {player.name} week {week or 'season'}")
            
            return True
            
        except Exception as e:
            print(f"   Error syncing stats for player {player_id}: {e}")
            return False
    
    def _update_weekly_score(self, score: WeeklyScore, stats: Dict[str, Any]):
        """Update weekly score with API stats"""
        # Extract stats from API response
        # Note: Field names may vary based on actual API response
        score.passing_yards = float(stats.get('passingYards', 0) or 0)
        score.passing_tds = int(stats.get('passingTouchdowns', 0) or 0)
        score.passing_interceptions = int(stats.get('passingInterceptions', 0) or 0)
        score.rushing_yards = float(stats.get('rushingYards', 0) or 0)
        score.rushing_tds = int(stats.get('rushingTouchdowns', 0) or 0)
        score.receiving_yards = float(stats.get('receivingYards', 0) or 0)
        score.receiving_tds = int(stats.get('receivingTouchdowns', 0) or 0)
        score.receptions = int(stats.get('receptions', 0) or 0)
        score.fumbles = int(stats.get('fumbles', 0) or 0)
        
        # Calculate fantasy points (basic calculation)
        score.fantasy_points = self._calculate_fantasy_points(score)
    
    def _calculate_fantasy_points(self, score: WeeklyScore) -> float:
        """Calculate fantasy points based on stats"""
        points = 0.0
        
        # Passing points
        points += (score.passing_yards / 25) * 0.04  # 1 point per 25 yards
        points += score.passing_tds * 4  # 4 points per TD
        points -= score.passing_interceptions * 2  # -2 points per INT
        
        # Rushing points
        points += (score.rushing_yards / 10) * 0.1  # 1 point per 10 yards
        points += score.rushing_tds * 6  # 6 points per TD
        
        # Receiving points
        points += (score.receiving_yards / 10) * 0.1  # 1 point per 10 yards
        points += score.receiving_tds * 6  # 6 points per TD
        points += score.receptions * 0.5  # 0.5 points per reception
        
        # Fumble penalty
        points -= score.fumbles * 2  # -2 points per fumble
        
        return round(points, 2)
    
    def sync_injury_data(self):
        """Sync injury data from API to database"""
        print("Syncing injury data...")
        
        try:
            injury_data = self.nfl_api.get_injury_report()
            
            if not injury_data:
                print("No injury data received from API")
                return False
            
            print(f"Found injury data for {len(injury_data)} players")
            
            # Update player injury status in database
            updated_count = 0
            with self.app.app_context():
                for injury in injury_data:
                    if self._update_player_injury_status(injury):
                        updated_count += 1
                
                self.db.session.commit()
            
            print(f"Successfully updated injury status for {updated_count} players")
            return True
            
        except Exception as e:
            print(f"Error syncing injury data: {e}")
            return False
    
    def _update_player_injury_status(self, injury: Dict[str, Any]) -> bool:
        """Update player injury status in database"""
        try:
            player_id = injury.get('playerId') or injury.get('id')
            if not player_id:
                return False
            
            # Find player in database
            player = NFLPlayer.query.filter_by(nfl_id=str(player_id)).first()
            if not player:
                return False
            
            # Update injury status
            player.is_injured = True
            player.injury_status = injury.get('status', 'Questionable')
            
            return True
            
        except Exception as e:
            print(f"   Error updating injury status for player {player_id}: {e}")
            return False
    
    def full_sync(self):
        """Perform full data synchronization"""
        print("Starting full data synchronization...")
        print("=" * 50)
        
        success = True
        
        # Sync teams
        if not self.sync_nfl_teams():
            success = False
        
        # Sync players
        if not self.sync_nfl_players():
            success = False
        
        # Sync current season stats
        if not self.sync_player_stats(2024):
            success = False
        
        # Sync injury data
        if not self.sync_injury_data():
            success = False
        
        print("=" * 50)
        if success:
            print("Full synchronization completed successfully!")
        else:
            print("Synchronization completed with some errors")
        
        return success

# Global instance for CLI usage
data_sync = DataSyncService()
