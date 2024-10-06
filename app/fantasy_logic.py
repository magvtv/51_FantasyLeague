from app import nfl_api, mongo

def draft_player(team_id, player_id):
    player_data = nfl_api.get_player_data(player_id)
    # Add logic to check if player is available, within salary cap, etc.
    mongo.db.fantasy_teams.update_one(
        {'_id': team_id},
        {'$push': {'players': player_id}}
    )

def calculate_team_score(team_id):
    team = mongo.db.fantasy_teams.find_one({'_id': team_id})
    total_points = 0
    for player_id in team['players']:
        player_stats = nfl_api.get_player_data(player_id)
        # Add logic to calculate points based on player stats
        total_points += calculate_player_points(player_stats)
    mongo.db.fantasy_teams.update_one(
        {'_id': team_id},
        {'$set': {'total_points': total_points}}
    )

def calculate_player_points(player_stats):
    # Implement your fantasy scoring logic here
    points = 0
    # Example: points for passing yards
    points += player_stats['passing_yards'] * 0.04
    # Add more scoring rules...
    return points