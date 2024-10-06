import requests
import json

def rapid_api_call():
    url = "https://nfl-api-data.p.rapidapi.com/nfl-team-listing/v1/data"

    headers = {
        "x-rapidapi-key": "16806452c5mshfb321706c9a62fbp118a73jsn7602a14f4b61",
        "x-rapidapi-host": "nfl-api-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    # Write the JSON response to a file with indentation
    with open('nfl_fantasy.json', 'w') as json_file:
        json.dump(response.json(), json_file, indent=4)

    print("Data has been written to nfl_fantasy.json")

rapid_api_call()
