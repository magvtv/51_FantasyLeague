import requests
from cachetools import TTLCache
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

load_dotenv()

class NFLApiService:
    def __init__(self):
        self.base_url = f"https://{os.getenv('RAPIDAPI_HOST', 'nfl-api-data.p.rapidapi.com')}"
        self.headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": os.getenv('RAPIDAPI_HOST', 'nfl-api-data.p.rapidapi.com')
        }
        self.cache = TTLCache(maxsize=1000, ttl=300)  # 5-minute cache
        
    def _get_request(self, endpoint, params=None):
        """Make cached GET request to NFL API"""
        cache_key = f"{endpoint}_{str(params)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            response = requests.get(f"{self.base_url}/{endpoint}", headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            self.cache[cache_key] = data
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from NFL API: {e}")
            return None

    # Working endpoints based on actual API testing
    def get_team_data(self, team_id=None):
        """Get NFL team data - all teams if no ID provided"""
        data = self._get_request("nfl-team-listing/v1/data")
        if not data:
            return None
        
        # Transform the data to match expected format
        teams = []
        for item in data:
            team_info = item.get('team', {})
            if team_id and str(team_info.get('id')) != str(team_id):
                continue
                
            teams.append({
                'id': team_info.get('id'),
                'name': team_info.get('displayName'),
                'abbreviation': team_info.get('abbreviation'),
                'location': team_info.get('location'),
                'nickname': team_info.get('nickname'),
                'color': team_info.get('color'),
                'is_active': team_info.get('isActive'),
                'logos': team_info.get('logos', [])
            })
        
        if team_id:
            return teams[0] if teams else None
        else:
            return {'teams': teams}
    
    def get_teams_list(self):
        """Get a simple list of all NFL teams"""
        data = self._get_request("nfl-team-listing/v1/data")
        if not data:
            return []
        
        teams = []
        for item in data:
            team_info = item.get('team', {})
            teams.append({
                'id': team_info.get('id'),
                'name': team_info.get('displayName'),
                'abbreviation': team_info.get('abbreviation'),
                'location': team_info.get('location'),
                'nickname': team_info.get('nickname')
            })
        
        return teams

    def get_players_by_team(self, team_id):
        """Get all players for a specific team"""
        # Try multiple endpoint patterns since the exact endpoint may vary
        endpoints_to_try = [
            f"nfl-team-roster/v1/data",
            f"nfl-team/{team_id}/roster",
            f"nfl-team-roster",
            f"nfl-players/team/{team_id}",
            f"nfl-team-players/{team_id}"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                params = {'teamId': team_id} if 'roster' in endpoint else {}
                data = self._get_request(endpoint, params)
                if data and isinstance(data, list) and len(data) > 0:
                    break
            except:
                continue
        else:
            # If no endpoints work, return empty result
            return {'players': [], 'message': 'No players found for this team'}
        
        players = []
        for item in data:
            if isinstance(item, dict):
                player_info = item.get('player', item)  # Try both nested and direct structure
                players.append({
                    'id': player_info.get('id', f"{team_id}_{player_info.get('name', 'unknown')}"),
                    'name': player_info.get('displayName', player_info.get('name', 'Unknown Player')),
                    'position': player_info.get('position', 'UNKNOWN'),
                    'team_id': team_id,
                    'jersey_number': player_info.get('jerseyNumber'),
                    'height': player_info.get('height'),
                    'weight': player_info.get('weight'),
                    'age': player_info.get('age'),
                    'experience': player_info.get('experience'),
                    'college': player_info.get('college', {}).get('name') if isinstance(player_info.get('college'), dict) else player_info.get('college')
                })
        
        return {'players': players}

    def get_season_stats(self, season=2024):
        """Get all player statistics for a specific season"""
        # Try multiple endpoint patterns
        endpoints_to_try = [
            f"nfl-season-stats/v1/data",
            f"nfl-stats/{season}",
            f"nfl-season/{season}/stats",
            f"nfl-player-stats/{season}"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                params = {'season': season} if 'stats' in endpoint else {}
                data = self._get_request(endpoint, params)
                if data and isinstance(data, list) and len(data) > 0:
                    break
            except:
                continue
        else:
            return {'players': [], 'message': f'No stats found for season {season}'}
        
        return {'players': data}

    def get_weekly_stats(self, season=2024, week=1):
        """Get all player statistics for a specific week"""
        # Try multiple endpoint patterns
        endpoints_to_try = [
            f"nfl-weekly-stats/v1/data",
            f"nfl-stats/{season}/week/{week}",
            f"nfl-week/{week}/stats",
            f"nfl-player-stats/{season}/{week}"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                params = {'season': season, 'week': week} if 'stats' in endpoint else {}
                data = self._get_request(endpoint, params)
                if data and isinstance(data, list) and len(data) > 0:
                    break
            except:
                continue
        else:
            return {'players': [], 'message': f'No stats found for week {week} season {season}'}
        
        return {'players': data}

    def get_injury_report(self):
        """Get current injury reports"""
        # Try multiple endpoint patterns
        endpoints_to_try = [
            f"nfl-injury-report/v1/data",
            f"nfl-injuries",
            f"nfl-injury-list",
            f"nfl-injured-players"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                data = self._get_request(endpoint)
                if data and isinstance(data, list) and len(data) > 0:
                    break
            except:
                continue
        else:
            return {'message': 'No injury report found'}
        
        return data

    def get_player_stats(self, player_id, season=2024, week=None):
        """Get detailed player statistics for a specific season and week"""
        # Try multiple endpoint patterns
        endpoints_to_try = [
            f"nfl-player-stats/v1/data",
            f"nfl-player/{player_id}/stats",
            f"nfl-player-stats/{player_id}",
            f"nfl-player/{player_id}/season/{season}"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                params = {'playerId': player_id, 'season': season}
                if week:
                    params['week'] = week
                data = self._get_request(endpoint, params)
                if data and isinstance(data, list) and len(data) > 0:
                    break
            except:
                continue
        else:
            return None
        
        return data[0] if data else None

    # Placeholder methods for endpoints that don't exist yet
    def get_current_season(self):
        """Get current NFL season information - Placeholder"""
        return {
            'season': 2024,
            'type': 'Regular Season',
            'status': 'Active',
            'message': 'This endpoint is not available in the current API'
        }
    
    def get_season_schedule(self, season=None):
        """Get complete season schedule - Placeholder"""
        return {
            'season': season or 2024,
            'message': 'Schedule endpoint is not available in the current API'
        }
    
    def get_weekly_schedule(self, season, week):
        """Get schedule for specific week - Placeholder"""
        return {
            'season': season,
            'week': week,
            'message': 'Weekly schedule endpoint is not available in the current API'
        }
    
    def get_daily_schedule(self, date):
        """Get schedule for specific date - Placeholder"""
        return {
            'date': date,
            'message': 'Daily schedule endpoint is not available in the current API'
        }
    
    def get_calendar(self):
        """Get NFL calendar/schedule - Placeholder"""
        return {
            'message': 'Calendar endpoint is not available in the current API'
        }

    def get_team_stats(self, team_id, season=None):
        """Get detailed team statistics - Placeholder"""
        return {
            'team_id': team_id,
            'season': season,
            'message': 'Team stats endpoint is not available in the current API'
        }
    
    def get_team_standings(self, season=None):
        """Get team standings/rankings - Placeholder"""
        return {
            'season': season,
            'message': 'Standings endpoint is not available in the current API'
        }
    
    def get_team_depth_chart(self, team_id):
        """Get team depth chart - Placeholder"""
        return {
            'team_id': team_id,
            'message': 'Depth chart endpoint is not available in the current API'
        }

    def get_player_data(self, player_id):
        """Get specific player data by ID - Placeholder"""
        return {
            'player_id': player_id,
            'message': 'Player data endpoint is not available in the current API'
        }
    
    def get_player_injuries(self, player_id=None):
        """Get player injury information - Placeholder"""
        return {
            'player_id': player_id,
            'message': 'Player injuries endpoint is not available in the current API'
        }

    def get_live_scores(self):
        """Get live game scores - Placeholder"""
        return {
            'message': 'Live scores endpoint is not available in the current API'
        }
    
    def get_games_by_week(self, season, week):
        """Get games for a specific week and season - Placeholder"""
        return {
            'season': season,
            'week': week,
            'message': 'Games by week endpoint is not available in the current API'
        }
    
    def get_game_details(self, game_id):
        """Get detailed game information - Placeholder"""
        return {
            'game_id': game_id,
            'message': 'Game details endpoint is not available in the current API'
        }
    
    def get_play_by_play(self, game_id):
        """Get play-by-play data for a game - Placeholder"""
        return {
            'game_id': game_id,
            'message': 'Play by play endpoint is not available in the current API'
        }
    
    def get_game_odds(self, game_id=None):
        """Get betting odds for games - Placeholder"""
        return {
            'game_id': game_id,
            'message': 'Game odds endpoint is not available in the current API'
        }

    def get_player_statistics(self, season, week=None, player_id=None):
        """Get player statistics for season/week - Placeholder"""
        return {
            'season': season,
            'week': week,
            'player_id': player_id,
            'message': 'Player statistics endpoint is not available in the current API'
        }
    
    def get_passing_stats(self, season=None, week=None):
        """Get passing statistics - Placeholder"""
        return {
            'season': season,
            'week': week,
            'message': 'Passing stats endpoint is not available in the current API'
        }
    
    def get_rushing_stats(self, season=None, week=None):
        """Get rushing statistics - Placeholder"""
        return {
            'season': season,
            'week': week,
            'message': 'Rushing stats endpoint is not available in the current API'
        }
    
    def get_receiving_stats(self, season=None, week=None):
        """Get receiving statistics - Placeholder"""
        return {
            'season': season,
            'week': week,
            'message': 'Receiving stats endpoint is not available in the current API'
        }
    
    def get_defensive_stats(self, season=None, week=None):
        """Get defensive statistics - Placeholder"""
        return {
            'season': season,
            'week': week,
            'message': 'Defensive stats endpoint is not available in the current API'
        }
    
    def get_kicking_stats(self, season=None, week=None):
        """Get kicking statistics - Placeholder"""
        return {
            'season': season,
            'week': week,
            'message': 'Kicking stats endpoint is not available in the current API'
        }

    def get_nfl_news(self, limit=10):
        """Get NFL news articles - Placeholder"""
        return {
            'limit': limit,
            'message': 'News endpoint is not available in the current API'
        }
    
    def get_team_news(self, team_id, limit=10):
        """Get news for specific team - Placeholder"""
        return {
            'team_id': team_id,
            'limit': limit,
            'message': 'Team news endpoint is not available in the current API'
        }
    
    def get_player_news(self, player_id, limit=10):
        """Get news for specific player - Placeholder"""
        return {
            'player_id': player_id,
            'limit': limit,
            'message': 'Player news endpoint is not available in the current API'
        }

    def get_game_predictions(self, game_id=None):
        """Get game predictions and analysis - Placeholder"""
        return {
            'game_id': game_id,
            'message': 'Game predictions endpoint is not available in the current API'
        }
    
    def get_player_projections(self, player_id=None, week=None):
        """Get player fantasy projections - Placeholder"""
        return {
            'player_id': player_id,
            'week': week,
            'message': 'Player projections endpoint is not available in the current API'
        }

    def get_fantasy_points(self, player_id, season=None, week=None):
        """Get calculated fantasy points for players - Placeholder"""
        return {
            'player_id': player_id,
            'season': season,
            'week': week,
            'message': 'Fantasy points endpoint is not available in the current API'
        }
    
    def get_fantasy_rankings(self, position=None, season=None, week=None):
        """Get fantasy rankings by position - Placeholder"""
        return {
            'position': position,
            'season': season,
            'week': week,
            'message': 'Fantasy rankings endpoint is not available in the current API'
        }

    def get_fixtures(self, season=None, team_id=None):
        """Get NFL fixtures/schedule - Placeholder"""
        return {
            'season': season,
            'team_id': team_id,
            'message': 'Fixtures endpoint is not available in the current API'
        }
    
    def get_league_standings(self, season=None):
        """Get league standings - Placeholder"""
        return {
            'season': season,
            'message': 'League standings endpoint is not available in the current API'
        }
    
    def get_player_details(self, player_id):
        """Get detailed player information - Placeholder"""
        return {
            'player_id': player_id,
            'message': 'Player details endpoint is not available in the current API'
        }
    
    def get_match_details(self, match_id):
        """Get detailed match information - Placeholder"""
        return {
            'match_id': match_id,
            'message': 'Match details endpoint is not available in the current API'
        }
    
    def get_odds(self, match_id=None):
        """Get betting odds - Placeholder"""
        return {
            'match_id': match_id,
            'message': 'Odds endpoint is not available in the current API'
        }

    def get_current_nfl_game_dates(self):
        """Get current NFL game dates"""
        return self._get_request("nfl-whitelist")

    def get_all_nfl_seasons(self):
        """Get all NFL seasons"""
        return self._get_request("nfl-season")

    def get_nfl_season_info(self, year=2025):
        """Get individual NFL season info"""
        return self._get_request("nfl-season", {"year": year})

    def get_all_nfl_teams(self):
        """Get all NFL teams"""
        return self._get_request("nfl-team-list")

    def get_single_nfl_team_info(self, team_id):
        """Get single NFL team info"""
        return self._get_request("nfl-team-info", {"teamId": team_id})

    def get_nfl_team_injuries(self, team_id):
        """Get NFL team injuries"""
        return self._get_request("nfl-team-injuries", {"teamId": team_id})

    def get_nfl_team_coaches(self, team_id):
        """Get NFL team coaches"""
        return self._get_request("nfl-team-coaches", {"teamId": team_id})

    def get_nfl_team_news(self, team_id):
        """Get NFL team news"""
        return self._get_request("nfl-team-news", {"teamId": team_id})

    def get_nfl_team_schedule(self, team_id):
        """Get NFL team schedule"""
        return self._get_request("nfl-team-schedule", {"teamId": team_id})

    def get_nfl_team_roster(self, team_id):
        """Get NFL team players/roster"""
        return self._get_request("nfl-team-roster", {"teamId": team_id})

    def get_nfl_player_full_info(self, player_id):
        """Get NFL player full info"""
        return self._get_request("nfl-ath-fullinfo", {"playerId": player_id})

    def get_nfl_player_stats(self, player_id):
        """Get player stats"""
        return self._get_request("nfl-ath-stats", {"playerId": player_id})

    def get_nfl_player_statistics(self, player_id):
        """Get player statistics"""
        return self._get_request("nfl-ath-statistics", {"playerId": player_id})

    def get_nfl_player_news(self, player_id):
        """Get player news"""
        return self._get_request("nfl-ath-news", {"playerId": player_id})

    def get_nfl_player_overview(self, player_id):
        """Get player overview"""
        return self._get_request("nfl-ath-overview", {"playerId": player_id})

    def get_nfl_plays_by_plays(self, game_id):
        """Get NFL plays by plays"""
        return self._get_request("nfl-plays", {"gameId": game_id})

    # Utility Methods
    def clear_cache(self):
        """Clear the API cache"""
        self.cache.clear()
    
    def get_cache_info(self):
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "ttl": self.cache.ttl
        }

# Global instance for CLI usage
nfl_api = NFLApiService()
