from app.api_service import nfl_api
import json

print("Testing nfl-team-roster/v1/data...")
data = nfl_api._get_request("nfl-team-roster/v1/data", {"teamId": 22})
print(json.dumps(data, indent=2)[:2000])

print("\nTesting nfl-team/22/roster...")
data2 = nfl_api._get_request("nfl-team/22/roster")
print(json.dumps(data2, indent=2)[:2000])
