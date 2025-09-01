import requests
from cachetools import TTLCache
import os
from dotenv import load_dotenv

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

    def get_current_season(self):
        """Get current NFL season information"""
        return self._get_request("current_season")
    
    def get_team_data(self, team_id=None):
        """Get NFL team data - all teams if no ID provided"""
        if team_id:
            return self._get_request(f"teams/{team_id}")
        return self._get_request("nfl-team-listing/v1/data")
    
    def get_player_data(self, player_id):
        """Get specific player data by ID"""
        return self._get_request(f"players/{player_id}")
    
    def get_players_by_team(self, team_id):
        """Get all players for a specific team"""
        return self._get_request("players", params={"team": team_id})
    
    def get_live_scores(self):
        """Get live game scores"""
        return self._get_request("live_scores")
    
    def get_games_by_week(self, season, week):
        """Get games for a specific week and season"""
        return self._get_request("games", params={"season": season, "week": week})
    
    def get_game_details(self, game_id):
        """Get detailed game information"""
        return self._get_request(f"games/{game_id}")
    
    def get_player_statistics(self, season, week=None, player_id=None):
        """Get player statistics for season/week"""
        params = {"season": season}
        if week:
            params["week"] = week
        if player_id:
            params["player_id"] = player_id
        return self._get_request("statistics", params=params)
    
    def get_calendar(self):
        """Get NFL calendar/schedule"""
        return self._get_request("calendar")
    
    def get_injury_report(self):
        """Get current injury reports"""
        return self._get_request("injuries")

# Global instance for CLI usage
nfl_api = NFLApiService()
