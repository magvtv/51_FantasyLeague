from .models import db, NFLPlayer, FantasyTeam, TeamPlayer, WeeklyScore, WeeklyLineup, Transfer
from .database import app

def calculate_player_points(weekly_score):
    """
    Calculate fantasy points based on NFL statistics
    Using standard PPR (Point Per Reception) scoring
    """
    points = 0.0
    
    # Passing stats
    points += (weekly_score.passing_yards / 25) * 1  # 1 point per 25 passing yards
    points += weekly_score.passing_tds * 4  # 4 points per passing TD
    points -= weekly_score.passing_interceptions * 2  # -2 for interceptions
    
    # Rushing stats
    points += (weekly_score.rushing_yards / 10) * 1  # 1 point per 10 rushing yards
    points += weekly_score.rushing_tds * 6  # 6 points per rushing TD
    
    # Receiving stats
    points += (weekly_score.receiving_yards / 10) * 1  # 1 point per 10 receiving yards
    points += weekly_score.receiving_tds * 6  # 6 points per receiving TD
    points += weekly_score.receptions * 1  # 1 point per reception (PPR)
    
    # Fumbles
    points -= weekly_score.fumbles * 2  # -2 for fumbles
    
    # Kicker stats
    points += weekly_score.field_goals_made * 3  # 3 points per field goal
    points += weekly_score.extra_points_made * 1  # 1 point per extra point
    
    # Defense stats
    points += weekly_score.def_touchdowns * 6  # 6 points per defensive TD
    points += weekly_score.def_interceptions * 2  # 2 points per interception
    points += weekly_score.def_fumble_recoveries * 2  # 2 points per fumble recovery
    points += weekly_score.def_safeties * 2  # 2 points per safety
    
    # Points allowed by defense
    points_allowed = weekly_score.def_points_allowed
    if points_allowed == 0:
        points += 10
    elif points_allowed <= 6:
        points += 7
    elif points_allowed <= 13:
        points += 4
    elif points_allowed <= 20:
        points += 1
    elif points_allowed <= 27:
        points += 0
    else:
        points -= 1
    
    return round(points, 2)

def draft_player(team_id, player_id):
    """Add a player to a fantasy team"""
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        player = NFLPlayer.query.get(player_id)
        
        if not team or not player:
            return {"success": False, "message": "Team or player not found"}
        
        # Check if player is already on team
        existing = TeamPlayer.query.filter_by(team_id=team_id, player_id=player_id).first()
        if existing:
            return {"success": False, "message": "Player already on team"}
        
        # Check budget
        if team.budget_remaining < player.price:
            return {"success": False, "message": "Insufficient budget"}
        
        # Check roster constraints
        team_players = TeamPlayer.query.filter_by(team_id=team_id).count()
        if team_players >= 15:  # Maximum 15 players
            return {"success": False, "message": "Team roster is full (15 players max)"}
        
        # Add player to team
        team_player = TeamPlayer(
            team_id=team_id,
            player_id=player_id,
            purchase_price=player.price
        )
        
        # Update budget
        team.budget_remaining -= player.price
        
        db.session.add(team_player)
        db.session.commit()
        
        return {
            "success": True, 
            "message": f"Successfully drafted {player.name}",
            "remaining_budget": team.budget_remaining
        }

def transfer_player(team_id, player_out_id, player_in_id, week, season):
    """Transfer a player (sell one, buy another)"""
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        player_out = NFLPlayer.query.get(player_out_id)
        player_in = NFLPlayer.query.get(player_in_id)
        
        if not all([team, player_out, player_in]):
            return {"success": False, "message": "Team or players not found"}
        
        # Check if player_out is on team
        team_player_out = TeamPlayer.query.filter_by(
            team_id=team_id, player_id=player_out_id
        ).first()
        if not team_player_out:
            return {"success": False, "message": "Player not on your team"}
        
        # Check budget for new player
        cost_difference = player_in.price - team_player_out.purchase_price
        if team.budget_remaining < cost_difference:
            return {"success": False, "message": "Insufficient budget for transfer"}
        
        # Check free transfers
        point_hit = 0
        if team.free_transfers <= 0:
            point_hit = -4  # -4 points for extra transfers
        
        # Execute transfer
        db.session.delete(team_player_out)
        
        new_team_player = TeamPlayer(
            team_id=team_id,
            player_id=player_in_id,
            purchase_price=player_in.price
        )
        
        transfer_record = Transfer(
            team_id=team_id,
            week=week,
            season=season,
            player_in_id=player_in_id,
            player_out_id=player_out_id,
            cost=cost_difference,
            point_hit=point_hit
        )
        
        # Update team budget and transfers
        team.budget_remaining -= cost_difference
        if team.free_transfers > 0:
            team.free_transfers -= 1
        
        db.session.add(new_team_player)
        db.session.add(transfer_record)
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Successfully transferred {player_out.name} for {player_in.name}",
            "point_hit": point_hit,
            "remaining_budget": team.budget_remaining,
            "free_transfers": team.free_transfers
        }

def calculate_team_score(team_id, week, season):
    """Calculate total team score for a specific week"""
    with app.app_context():
        lineup = WeeklyLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if not lineup:
            return {"success": False, "message": "No lineup set for this week"}
        
        total_points = 0.0
        position_points = {}
        
        # Get scores for each position
        positions = [
            ('QB', lineup.qb_id), ('RB1', lineup.rb1_id), ('RB2', lineup.rb2_id),
            ('WR1', lineup.wr1_id), ('WR2', lineup.wr2_id), ('TE', lineup.te_id),
            ('K', lineup.k_id), ('DEF', lineup.def_id)
        ]
        
        for pos_name, player_id in positions:
            if player_id:
                weekly_score = WeeklyScore.query.filter_by(
                    player_id=player_id, week=week, season=season
                ).first()
                
                if weekly_score:
                    points = weekly_score.fantasy_points
                    total_points += points
                    position_points[pos_name] = {
                        'player_id': player_id,
                        'points': points
                    }
        
        # Update lineup total
        lineup.total_points = total_points
        db.session.commit()
        
        return {
            "success": True,
            "total_points": total_points,
            "position_breakdown": position_points
        }

def validate_lineup(team_id, lineup_data):
    """Validate a weekly lineup meets position requirements"""
    required_positions = ['qb_id', 'rb1_id', 'rb2_id', 'wr1_id', 'wr2_id', 'te_id', 'k_id', 'def_id']
    
    # Check all positions are filled
    for pos in required_positions:
        if not lineup_data.get(pos):
            return {"valid": False, "message": f"Missing {pos.replace('_id', '').upper()}"}
    
    # Check all players are on team
    with app.app_context():
        player_ids = [lineup_data[pos] for pos in required_positions if lineup_data.get(pos)]
        team_players = TeamPlayer.query.filter(
            TeamPlayer.team_id == team_id,
            TeamPlayer.player_id.in_(player_ids)
        ).all()
        
        if len(team_players) != len(player_ids):
            return {"valid": False, "message": "Some players are not on your team"}
    
    return {"valid": True, "message": "Lineup is valid"}

def get_team_summary(team_id):
    """Get comprehensive team summary"""
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        if not team:
            return None
        
        players = db.session.query(TeamPlayer, NFLPlayer).join(
            NFLPlayer, TeamPlayer.player_id == NFLPlayer.id
        ).filter(TeamPlayer.team_id == team_id).all()
        
        summary = {
            "team_name": team.name,
            "budget_remaining": team.budget_remaining,
            "total_players": len(players),
            "free_transfers": team.free_transfers,
            "players": []
        }
        
        for team_player, nfl_player in players:
            summary["players"].append({
                "id": nfl_player.id,
                "name": nfl_player.name,
                "position": nfl_player.position,
                "team": nfl_player.team,
                "price": nfl_player.price,
                "purchase_price": team_player.purchase_price,
                "total_points": nfl_player.total_points,
                "is_injured": nfl_player.is_injured
            })
        
        return summary
