import requests
from cachetools import TTLCache
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
api_host = os.getenv("API_HOST")


class NFLApiService:
    def __init__(self):
        self.base_url = "https://nfl-api-data.p.rapidapi.com/"
        self.headers = {
            "x-rapidapi-Key": api_key,
            "x-rapidapi-Host": api_host
        }
        self.cache = TTLCache(maxsize = 1000, ttl = 300)
        
    def _get_request(self, endpoint, params=None):
        cache_key = f"{endpoint}_{str(params)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        response = requests.get(f"{self.base_url}/{endpoint}", headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        self.cache[cache_key] = data
        return data

    def get_current_season(self):
        return self._get_request("current_season")
    
    
    # fetch nfl team data - would be nice to get by name
    def get_team_data(self, team_id):
        return self._get_request(f"teams/{team_id}")
    
    # fetch nfl player - get by name
    def get_player_data(self, player_id):
        return self._get_request(f"players/{player_id}")
    
    def get_live_scores(self):
        return self._get_request("live_scores")
    
    def get_games_by_week(self, season, week):
        return self._get_request("games", params={"season": season, "week": week})
    
    def get_game_details(self, game_id):
        return self._get_request(f"games/{game_id}")
    
    def get_statistics(self, season):
        return self._get_request("statistics", params={"season": season})
    
    def get_calendar(self):
        return self._get_request("calendar")