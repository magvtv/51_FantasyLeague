try:
    from .database import db
except ImportError:
    from database import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to fantasy teams
    fantasy_teams = db.relationship('FantasyTeam', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class NFLPlayer(db.Model):
    __tablename__ = 'nfl_players'
    
    id = db.Column(db.Integer, primary_key=True)
    nfl_id = db.Column(db.String(50), unique=True, nullable=False)  # External NFL API ID
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(10), nullable=False)  # QB, RB, WR, TE, K, DEF
    team = db.Column(db.String(10), nullable=False)  # NFL team abbreviation
    price = db.Column(db.Float, nullable=False, default=5000000)  # Price in fantasy budget
    total_points = db.Column(db.Float, default=0.0)
    is_injured = db.Column(db.Boolean, default=False)
    injury_status = db.Column(db.String(50))  # Questionable, Doubtful, Out, etc.
    
    # Relationship to weekly scores
    weekly_scores = db.relationship('WeeklyScore', backref='player', lazy=True)
    
    def __repr__(self):
        return f'<NFLPlayer {self.name} ({self.position})>'

class FantasyTeam(db.Model):
    __tablename__ = 'fantasy_teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    budget_remaining = db.Column(db.Float, default=100000000)  # $100M starting budget
    total_points = db.Column(db.Float, default=0.0)
    free_transfers = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to team players
    team_players = db.relationship('TeamPlayer', backref='team', lazy=True)
    weekly_lineups = db.relationship('WeeklyLineup', backref='team', lazy=True)
    transfers = db.relationship('Transfer', backref='team', lazy=True)
    
    def __repr__(self):
        return f'<FantasyTeam {self.name}>'

class TeamPlayer(db.Model):
    __tablename__ = 'team_players'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'), nullable=False)
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_price = db.Column(db.Float, nullable=False)
    
    # Ensure unique player per team
    __table_args__ = (UniqueConstraint('team_id', 'player_id'),)
    
    # Relationship to player details
    player = db.relationship('NFLPlayer', backref='fantasy_teams')
    
    def __repr__(self):
        return f'<TeamPlayer team:{self.team_id} player:{self.player_id}>'

class WeeklyLineup(db.Model):
    __tablename__ = 'weekly_lineups'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    
    # Starting lineup positions
    qb_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    rb1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    rb2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    wr1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    wr2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    te_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    k_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    def_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    
    total_points = db.Column(db.Float, default=0.0)
    is_finalized = db.Column(db.Boolean, default=False)
    
    # Chips and Captain
    captain_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    chip_used = db.Column(db.String(20))  # 'triple_captain', 'bench_boost', or None

    # Ensure unique lineup per team per week
    __table_args__ = (UniqueConstraint('team_id', 'week', 'season'),)
    
    def __repr__(self):
        return f'<WeeklyLineup team:{self.team_id} week:{self.week}>'

class WeeklyScore(db.Model):
    __tablename__ = 'weekly_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    
    # NFL Statistics
    passing_yards = db.Column(db.Float, default=0.0)
    passing_tds = db.Column(db.Integer, default=0)
    passing_interceptions = db.Column(db.Integer, default=0)
    rushing_yards = db.Column(db.Float, default=0.0)
    rushing_tds = db.Column(db.Integer, default=0)
    receiving_yards = db.Column(db.Float, default=0.0)
    receiving_tds = db.Column(db.Integer, default=0)
    receptions = db.Column(db.Integer, default=0)
    fumbles = db.Column(db.Integer, default=0)
    
    # Kicker stats
    field_goals_made = db.Column(db.Integer, default=0)
    field_goals_attempted = db.Column(db.Integer, default=0)
    extra_points_made = db.Column(db.Integer, default=0)
    
    # Defense stats
    def_touchdowns = db.Column(db.Integer, default=0)
    def_interceptions = db.Column(db.Integer, default=0)
    def_fumble_recoveries = db.Column(db.Integer, default=0)
    def_safeties = db.Column(db.Integer, default=0)
    def_points_allowed = db.Column(db.Integer, default=0)
    
    # Fantasy points
    fantasy_points = db.Column(db.Float, default=0.0)
    
    # Ensure unique score per player per week
    __table_args__ = (UniqueConstraint('player_id', 'week', 'season'),)
    
    def __repr__(self):
        return f'<WeeklyScore player:{self.player_id} week:{self.week} pts:{self.fantasy_points}>'

class Transfer(db.Model):
    __tablename__ = 'transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    
    player_in_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'), nullable=False)
    player_out_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'), nullable=False)
    
    cost = db.Column(db.Float, default=0.0)  # Cost if using extra transfer
    point_hit = db.Column(db.Integer, default=0)  # -4 for extra transfers
    
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transfer team:{self.team_id} week:{self.week}>'

class NFLTeam(db.Model):
    __tablename__ = 'nfl_teams'
    
    id = db.Column(db.Integer, primary_key=True)
    team_code = db.Column(db.String(10), unique=True, nullable=False)  # TB, KC, etc.
    team_name = db.Column(db.String(100), nullable=False)  # Tampa Bay Buccaneers
    city = db.Column(db.String(50), nullable=False)  # Tampa Bay
    nickname = db.Column(db.String(50), nullable=False)  # Buccaneers
    
    def __repr__(self):
        return f'<NFLTeam {self.team_name}>'

class OffenseLineup(db.Model):
    __tablename__ = 'offense_lineups'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    
    # Offensive positions
    qb_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    rb1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    rb2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    wr1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    wr2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    te_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    
    # Points tracking
    offense_points = db.Column(db.Float, default=0.0)
    is_finalized = db.Column(db.Boolean, default=False)
    
    # Ensure unique lineup per team per week
    __table_args__ = (UniqueConstraint('team_id', 'week', 'season'),)
    
    def __repr__(self):
        return f'<OffenseLineup team:{self.team_id} week:{self.week}>'

class DefenseLineup(db.Model):
    __tablename__ = 'defense_lineups'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    
    # Defense can be either individual players or entire team
    selection_type = db.Column(db.String(20), nullable=False)  # 'individual' or 'team'
    
    # For individual player selection
    dl1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))  # Defensive Line
    dl2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    lb1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))  # Linebacker
    lb2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    cb1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))  # Cornerback
    cb2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    s1_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))   # Safety
    s2_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    
    # For team selection
    nfl_team_id = db.Column(db.Integer, db.ForeignKey('nfl_teams.id'))
    
    # Points tracking
    defense_points = db.Column(db.Float, default=0.0)
    is_finalized = db.Column(db.Boolean, default=False)
    
    # Ensure unique lineup per team per week
    __table_args__ = (UniqueConstraint('team_id', 'week', 'season'),)
    
    def __repr__(self):
        return f'<DefenseLineup team:{self.team_id} week:{self.week}>'

class SpecialTeamsLineup(db.Model):
    __tablename__ = 'special_teams_lineups'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('fantasy_teams.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    season = db.Column(db.Integer, nullable=False)
    
    # Special teams can be either individual players or entire team
    selection_type = db.Column(db.String(20), nullable=False)  # 'individual' or 'team'
    
    # For individual player selection
    kicker_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    punter_id = db.Column(db.Integer, db.ForeignKey('nfl_players.id'))
    
    # For team selection
    nfl_team_id = db.Column(db.Integer, db.ForeignKey('nfl_teams.id'))
    
    # Points tracking
    special_teams_points = db.Column(db.Float, default=0.0)
    is_finalized = db.Column(db.Boolean, default=False)
    
    # Ensure unique lineup per team per week
    __table_args__ = (UniqueConstraint('team_id', 'week', 'season'),)
    
    def __repr__(self):
        return f'<SpecialTeamsLineup team:{self.team_id} week:{self.week}>'
