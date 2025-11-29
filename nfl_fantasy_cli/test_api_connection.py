import os
import requests
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = "nfl-api-data.p.rapidapi.com"

if not RAPIDAPI_KEY:
    print("❌ RAPIDAPI_KEY not found in .env file")
    sys.exit(1)

def test_endpoint(name, url, params=None):
    print(f"\nTesting {name}...")
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            # Print a snippet of data
            print(f"Response snippet: {str(data)[:200]}...")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🏈 Testing NFL API Connection...")
    print(f"API Key: {'*' * (len(RAPIDAPI_KEY)-4) + RAPIDAPI_KEY[-4:] if RAPIDAPI_KEY else 'Missing'}")
    
    # Test 1: Season Info (GET)
    test_endpoint(
        "Season Info", 
        "https://nfl-api-data.p.rapidapi.com/nfl-season",
        params={"year": "2024"}
    )
    
    # Test 2: Teams (GET List)
    test_endpoint(
        "Teams List",
        "https://nfl-api-data.p.rapidapi.com/nfl-team-list"
    )
    
    # Test 3: Live Scores (GET Whitelist/Dates)
    test_endpoint(
        "Game Dates",
        "https://nfl-api-data.p.rapidapi.com/nfl-whitelist"
    )

if __name__ == "__main__":
    main()
