#!/usr/bin/env python3
"""
Prefill Tampa Bay Buccaneers data for weeks 1-8
This script creates historical lineups using Tampa Bay players for the first 8 weeks
"""

import os
import sys
import random
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from database import get_app, get_db
from models import (
    NFLPlayer, NFLTeam, OffenseLineup, DefenseLineup, SpecialTeamsLineup, 
    WeeklyScore, FantasyTeam, User
)

def create_tampa_bay_players():
    """Create Tampa Bay Buccaneers players if they don't exist"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        # Tampa Bay Buccaneers players (2024 roster)
        tampa_players = [
            # Offense
            {'name': 'Baker Mayfield', 'position': 'QB', 'team': 'TB', 'price': 8000000},
            {'name': 'Rachaad White', 'position': 'RB', 'team': 'TB', 'price': 7000000},
            {'name': 'Chase Edmonds', 'position': 'RB', 'team': 'TB', 'price': 4000000},
            {'name': 'Mike Evans', 'position': 'WR', 'team': 'TB', 'price': 9000000},
            {'name': 'Chris Godwin', 'position': 'WR', 'team': 'TB', 'price': 8000000},
            {'name': 'Cade Otton', 'position': 'TE', 'team': 'TB', 'price': 5000000},
            
            # Defense
            {'name': 'Vita Vea', 'position': 'DL', 'team': 'TB', 'price': 6000000},
            {'name': 'Calijah Kancey', 'position': 'DL', 'team': 'TB', 'price': 5000000},
            {'name': 'Lavonte David', 'position': 'LB', 'team': 'TB', 'price': 7000000},
            {'name': 'Devin White', 'position': 'LB', 'team': 'TB', 'price': 6500000},
            {'name': 'Carlton Davis', 'position': 'CB', 'team': 'TB', 'price': 5500000},
            {'name': 'Jamel Dean', 'position': 'CB', 'team': 'TB', 'price': 5000000},
            {'name': 'Antoine Winfield Jr.', 'position': 'S', 'team': 'TB', 'price': 6000000},
            {'name': 'Ryan Neal', 'position': 'S', 'team': 'TB', 'price': 4000000},
            
            # Special Teams
            {'name': 'Chase McLaughlin', 'position': 'K', 'team': 'TB', 'price': 3000000},
            {'name': 'Jake Camarda', 'position': 'P', 'team': 'TB', 'price': 2000000},
            
            # Team Defense
            {'name': 'Tampa Bay Buccaneers Defense', 'position': 'DEF', 'team': 'TB', 'price': 5500000}
        ]
        
        created_players = []
        for player_data in tampa_players:
            # Check if player already exists
            existing = NFLPlayer.query.filter_by(
                name=player_data['name'], 
                team=player_data['team']
            ).first()
            
            if not existing:
                player = NFLPlayer(
                    nfl_id=f"tb_{player_data['name'].lower().replace(' ', '_')}",
                    name=player_data['name'],
                    position=player_data['position'],
                    team=player_data['team'],
                    price=player_data['price'],
                    total_points=0.0
                )
                db.session.add(player)
                created_players.append(player)
            else:
                created_players.append(existing)
        
        db.session.commit()
        print(f"✅ Created/verified {len(created_players)} Tampa Bay players")
        return created_players

def generate_weekly_stats(player, week, season):
    """Generate realistic weekly stats for a player"""
    stats = {
        'passing_yards': 0.0,
        'passing_tds': 0,
        'passing_interceptions': 0,
        'rushing_yards': 0.0,
        'rushing_tds': 0,
        'receiving_yards': 0.0,
        'receiving_tds': 0,
        'receptions': 0,
        'fumbles': 0,
        'field_goals_made': 0,
        'field_goals_attempted': 0,
        'extra_points_made': 0,
        'def_touchdowns': 0,
        'def_interceptions': 0,
        'def_fumble_recoveries': 0,
        'def_safeties': 0,
        'def_points_allowed': 0,
        'fantasy_points': 0.0
    }
    
    position = player.position
    
    if position == 'QB':
        stats['passing_yards'] = random.randint(180, 350)
        stats['passing_tds'] = random.randint(1, 4)
        stats['passing_interceptions'] = random.randint(0, 2)
        stats['rushing_yards'] = random.randint(0, 30)
        stats['rushing_tds'] = random.randint(0, 1)
        
    elif position == 'RB':
        stats['rushing_yards'] = random.randint(50, 120)
        stats['rushing_tds'] = random.randint(0, 2)
        stats['receiving_yards'] = random.randint(10, 50)
        stats['receiving_tds'] = random.randint(0, 1)
        stats['receptions'] = random.randint(2, 6)
        
    elif position == 'WR':
        stats['receiving_yards'] = random.randint(40, 120)
        stats['receiving_tds'] = random.randint(0, 2)
        stats['receptions'] = random.randint(3, 8)
        stats['rushing_yards'] = random.randint(0, 20)
        
    elif position == 'TE':
        stats['receiving_yards'] = random.randint(20, 80)
        stats['receiving_tds'] = random.randint(0, 1)
        stats['receptions'] = random.randint(2, 6)
        
    elif position == 'K':
        stats['field_goals_made'] = random.randint(1, 3)
        stats['field_goals_attempted'] = stats['field_goals_made'] + random.randint(0, 1)
        stats['extra_points_made'] = random.randint(2, 5)
        
    elif position == 'P':
        # Punters don't typically score fantasy points in standard leagues
        pass
        
    elif position == 'DL':
        stats['def_interceptions'] = random.randint(0, 1)
        stats['def_fumble_recoveries'] = random.randint(0, 1)
        
    elif position == 'LB':
        stats['def_interceptions'] = random.randint(0, 1)
        stats['def_fumble_recoveries'] = random.randint(0, 1)
        
    elif position == 'CB':
        stats['def_interceptions'] = random.randint(0, 2)
        
    elif position == 'S':
        stats['def_interceptions'] = random.randint(0, 1)
        stats['def_fumble_recoveries'] = random.randint(0, 1)
        
    elif position == 'DEF':
        stats['def_touchdowns'] = random.randint(0, 1)
        stats['def_interceptions'] = random.randint(0, 3)
        stats['def_fumble_recoveries'] = random.randint(0, 2)
        stats['def_safeties'] = random.randint(0, 1)
        stats['def_points_allowed'] = random.randint(7, 28)
    
    # Calculate fantasy points (simplified PPR scoring)
    fantasy_points = 0.0
    
    # Passing
    fantasy_points += (stats['passing_yards'] / 25) * 1
    fantasy_points += stats['passing_tds'] * 4
    fantasy_points -= stats['passing_interceptions'] * 2
    
    # Rushing
    fantasy_points += (stats['rushing_yards'] / 10) * 1
    fantasy_points += stats['rushing_tds'] * 6
    
    # Receiving
    fantasy_points += (stats['receiving_yards'] / 10) * 1
    fantasy_points += stats['receiving_tds'] * 6
    fantasy_points += stats['receptions'] * 1  # PPR
    
    # Fumbles
    fantasy_points -= stats['fumbles'] * 2
    
    # Kicking
    fantasy_points += stats['field_goals_made'] * 3
    fantasy_points += stats['extra_points_made'] * 1
    
    # Defense
    fantasy_points += stats['def_touchdowns'] * 6
    fantasy_points += stats['def_interceptions'] * 2
    fantasy_points += stats['def_fumble_recoveries'] * 2
    fantasy_points += stats['def_safeties'] * 2
    
    # Points allowed by defense
    points_allowed = stats['def_points_allowed']
    if points_allowed == 0:
        fantasy_points += 10
    elif points_allowed <= 6:
        fantasy_points += 7
    elif points_allowed <= 13:
        fantasy_points += 4
    elif points_allowed <= 20:
        fantasy_points += 1
    elif points_allowed <= 27:
        fantasy_points += 0
    else:
        fantasy_points -= 1
    
    stats['fantasy_points'] = round(fantasy_points, 2)
    return stats

def create_weekly_scores(players, weeks, season):
    """Create weekly scores for Tampa Bay players"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        created_scores = []
        
        for week in weeks:
            for player in players:
                # Check if score already exists
                existing = WeeklyScore.query.filter_by(
                    player_id=player.id, week=week, season=season
                ).first()
                
                if not existing:
                    stats = generate_weekly_stats(player, week, season)
                    
                    score = WeeklyScore(
                        player_id=player.id,
                        week=week,
                        season=season,
                        **stats
                    )
                    
                    db.session.add(score)
                    created_scores.append(score)
                    
                    # Update player's total points
                    player.total_points += stats['fantasy_points']
        
        db.session.commit()
        print(f"✅ Created {len(created_scores)} weekly scores for weeks {min(weeks)}-{max(weeks)}")
        return created_scores

def create_tampa_bay_lineups(team_id, weeks, season):
    """Create Tampa Bay lineups for the specified weeks"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        # Get Tampa Bay players
        tb_players = NFLPlayer.query.filter_by(team='TB').all()
        
        # Create player lookup by position
        players_by_pos = {}
        for player in tb_players:
            if player.position not in players_by_pos:
                players_by_pos[player.position] = []
            players_by_pos[player.position].append(player)
        
        created_lineups = []
        
        for week in weeks:
            # Create offense lineup
            offense_data = {
                'qb_id': players_by_pos.get('QB', [None])[0].id if players_by_pos.get('QB') else None,
                'rb1_id': players_by_pos.get('RB', [None])[0].id if players_by_pos.get('RB') else None,
                'rb2_id': players_by_pos.get('RB', [None])[1].id if len(players_by_pos.get('RB', [])) > 1 else None,
                'wr1_id': players_by_pos.get('WR', [None])[0].id if players_by_pos.get('WR') else None,
                'wr2_id': players_by_pos.get('WR', [None])[1].id if len(players_by_pos.get('WR', [])) > 1 else None,
                'te_id': players_by_pos.get('TE', [None])[0].id if players_by_pos.get('TE') else None
            }
            
            offense_lineup = OffenseLineup(
                team_id=team_id,
                week=week,
                season=season,
                **offense_data
            )
            db.session.add(offense_lineup)
            created_lineups.append(offense_lineup)
            
            # Create defense lineup (team selection)
            tb_team = NFLTeam.query.filter_by(team_code='TB').first()
            defense_data = {
                'selection_type': 'team',
                'nfl_team_id': tb_team.id if tb_team else None
            }
            
            defense_lineup = DefenseLineup(
                team_id=team_id,
                week=week,
                season=season,
                **defense_data
            )
            db.session.add(defense_lineup)
            created_lineups.append(defense_lineup)
            
            # Create special teams lineup (team selection)
            special_data = {
                'selection_type': 'team',
                'nfl_team_id': tb_team.id if tb_team else None
            }
            
            special_lineup = SpecialTeamsLineup(
                team_id=team_id,
                week=week,
                season=season,
                **special_data
            )
            db.session.add(special_lineup)
            created_lineups.append(special_lineup)
        
        db.session.commit()
        print(f"✅ Created {len(created_lineups)} lineups for weeks {min(weeks)}-{max(weeks)}")
        return created_lineups

def main():
    """Main function to prefill Tampa Bay data"""
    print("🚀 Tampa Bay Buccaneers Data Prefill Script")
    print("=" * 50)
    
    # Configuration
    weeks_to_fill = list(range(1, 9))  # Weeks 1-8
    season = 2024
    
    try:
        # Create Tampa Bay players
        players = create_tampa_bay_players()
        
        # Create weekly scores
        weekly_scores = create_weekly_scores(players, weeks_to_fill, season)
        
        # Get or create a test team
        app = get_app()
        db = get_db()
        
        with app.app_context():
            # Get first user or create one
            user = User.query.first()
            if not user:
                user = User(username='tampa_fan', email='tampa@example.com')
                db.session.add(user)
                db.session.commit()
            
            # Get or create fantasy team
            team = FantasyTeam.query.filter_by(user_id=user.id).first()
            if not team:
                team = FantasyTeam(
                    name='Tampa Bay Buccaneers',
                    user_id=user.id,
                    budget_remaining=100000000
                )
                db.session.add(team)
                db.session.commit()
            
            print(f"📊 Using team: {team.name} (ID: {team.id})")
            
            # Create lineups
            lineups = create_tampa_bay_lineups(team.id, weeks_to_fill, season)
        
        print("=" * 50)
        print("🎉 Tampa Bay data prefill completed successfully!")
        print(f"📈 Created data for weeks {min(weeks_to_fill)}-{max(weeks_to_fill)}")
        print(f"👥 {len(players)} players")
        print(f"📊 {len(weekly_scores)} weekly scores")
        print(f"🏈 {len(lineups)} lineups")
        print("\n💡 You can now start selecting your own lineups from week 9!")
        
    except Exception as e:
        print(f"❌ Error during prefill: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
