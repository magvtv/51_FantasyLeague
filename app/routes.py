from flask import jsonify, request
from app import app, mongo, jwt, nfl_api
from app.models import User, FantasyTeam
from app.fantasy_logic import draft_player, calculate_team_score

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    User.create(data['username'], data['email'], data['password'])
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/create_team', methods=['POST'])
def create_team():
    data = request.json
    FantasyTeam.create(data['user_id'], data['team_name'])
    return jsonify({'message': 'Team created successfully'}), 201

@app.route('/draft_player', methods=['POST'])
def draft_player_route():
    data = request.json
    draft_player(data['team_id'], data['player_id'])
    return jsonify({'message': 'Player drafted successfully'}), 200

@app.route('/team_score/<team_id>', methods=['GET'])
def get_team_score(team_id):
    calculate_team_score(team_id)
    team = mongo.db.fantasy_teams.find_one({'_id': team_id})
    return jsonify({'team_name': team['team_name'], 'total_points': team['total_points']})

@app.route('/live_scores', methods=['GET'])
def get_live_scores():
    scores = nfl_api.get_live_scores()
    return jsonify(scores)