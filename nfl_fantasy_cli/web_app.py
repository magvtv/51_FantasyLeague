from flask import render_template, request, redirect, url_for
from app.database import get_app, db
from app.models import User, FantasyTeam, NFLPlayer, WeeklyLineup, WeeklyScore
from sqlalchemy import func, desc

import os

# Get the Flask app instance from the existing factory
app = get_app()

# Configure template and static folders to be relative to this script
basedir = os.path.abspath(os.path.dirname(__file__))
app.template_folder = os.path.join(basedir, 'templates')
app.static_folder = os.path.join(basedir, 'static')

@app.route('/')
def index():
    user_count = User.query.count()
    team_count = FantasyTeam.query.count()
    player_count = NFLPlayer.query.count()
    
    # Get top 5 teams by total points
    top_teams = FantasyTeam.query.order_by(FantasyTeam.total_points.desc()).limit(5).all()
    
    return render_template('index.html', 
                          user_count=user_count, 
                          team_count=team_count, 
                          player_count=player_count,
                          top_teams=top_teams)

@app.route('/leaderboard')
def leaderboard():
    teams = FantasyTeam.query.order_by(FantasyTeam.total_points.desc()).all()
    return render_template('leaderboard.html', teams=teams)

@app.route('/teams')
def teams():
    teams = FantasyTeam.query.order_by(FantasyTeam.name).all()
    return render_template('teams.html', teams=teams)

@app.route('/team/<int:team_id>')
def team_detail(team_id):
    team = FantasyTeam.query.get_or_404(team_id)
    players = team.team_players
    return render_template('team_detail.html', team=team, players=players)

@app.route('/players')
def players():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    position = request.args.get('position', '')
    
    query = NFLPlayer.query
    
    if search:
        query = query.filter(NFLPlayer.name.ilike(f'%{search}%'))
    
    if position:
        query = query.filter(NFLPlayer.position == position)
        
    pagination = query.order_by(NFLPlayer.price.desc()).paginate(page=page, per_page=20)
    
    return render_template('players.html', pagination=pagination, search=search, position=position)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
