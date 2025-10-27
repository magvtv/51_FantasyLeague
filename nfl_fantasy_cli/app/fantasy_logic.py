try:
    from .models import db, NFLPlayer, FantasyTeam, TeamPlayer, WeeklyScore, WeeklyLineup, Transfer, OffenseLineup, DefenseLineup, SpecialTeamsLineup, NFLTeam
    from .database import app
except ImportError:
    from models import db, NFLPlayer, FantasyTeam, TeamPlayer, WeeklyScore, WeeklyLineup, Transfer, OffenseLineup, DefenseLineup, SpecialTeamsLineup, NFLTeam
    from database import app

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

# =============================================================================
# MODULAR TEAM CALCULATION FUNCTIONS
# =============================================================================

def calculate_offense_points(team_id, week, season):
    """Calculate total offense points for a team in a specific week"""
    with app.app_context():
        offense_lineup = OffenseLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if not offense_lineup:
            return {"success": False, "message": "No offense lineup set for this week"}
        
        total_points = 0.0
        position_points = {}
        
        # Get scores for each offensive position
        positions = [
            ('QB', offense_lineup.qb_id),
            ('RB1', offense_lineup.rb1_id),
            ('RB2', offense_lineup.rb2_id),
            ('WR1', offense_lineup.wr1_id),
            ('WR2', offense_lineup.wr2_id),
            ('TE', offense_lineup.te_id)
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
        
        # Update offense lineup total
        offense_lineup.offense_points = total_points
        db.session.commit()
        
        return {
            "success": True,
            "offense_points": total_points,
            "position_breakdown": position_points
        }

def calculate_defense_points(team_id, week, season):
    """Calculate total defense points for a team in a specific week"""
    with app.app_context():
        defense_lineup = DefenseLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if not defense_lineup:
            return {"success": False, "message": "No defense lineup set for this week"}
        
        total_points = 0.0
        position_points = {}
        
        if defense_lineup.selection_type == 'individual':
            # Calculate points for individual defensive players
            positions = [
                ('DL1', defense_lineup.dl1_id),
                ('DL2', defense_lineup.dl2_id),
                ('LB1', defense_lineup.lb1_id),
                ('LB2', defense_lineup.lb2_id),
                ('CB1', defense_lineup.cb1_id),
                ('CB2', defense_lineup.cb2_id),
                ('S1', defense_lineup.s1_id),
                ('S2', defense_lineup.s2_id)
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
        
        elif defense_lineup.selection_type == 'team':
            # Calculate points for team defense
            # This would need to be implemented based on team defense scoring
            # For now, we'll use a simplified approach
            nfl_team = NFLTeam.query.get(defense_lineup.nfl_team_id)
            if nfl_team:
                # Get team defense player (if exists in nfl_players with position='DEF')
                team_def_player = NFLPlayer.query.filter_by(
                    team=nfl_team.team_code, position='DEF'
                ).first()
                
                if team_def_player:
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=team_def_player.id, week=week, season=season
                    ).first()
                    
                    if weekly_score:
                        total_points = weekly_score.fantasy_points
                        position_points['TEAM_DEF'] = {
                            'player_id': team_def_player.id,
                            'points': total_points,
                            'team': nfl_team.team_name
                        }
        
        # Update defense lineup total
        defense_lineup.defense_points = total_points
        db.session.commit()
        
        return {
            "success": True,
            "defense_points": total_points,
            "position_breakdown": position_points
        }

def calculate_special_teams_points(team_id, week, season):
    """Calculate total special teams points for a team in a specific week"""
    with app.app_context():
        special_lineup = SpecialTeamsLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if not special_lineup:
            return {"success": False, "message": "No special teams lineup set for this week"}
        
        total_points = 0.0
        position_points = {}
        
        if special_lineup.selection_type == 'individual':
            # Calculate points for individual special teams players
            positions = [
                ('K', special_lineup.kicker_id),
                ('P', special_lineup.punter_id)
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
        
        elif special_lineup.selection_type == 'team':
            # Calculate points for team special teams
            nfl_team = NFLTeam.query.get(special_lineup.nfl_team_id)
            if nfl_team:
                # Get special teams players from the team
                kicker = NFLPlayer.query.filter_by(
                    team=nfl_team.team_code, position='K'
                ).first()
                punter = NFLPlayer.query.filter_by(
                    team=nfl_team.team_code, position='P'
                ).first()
                
                if kicker:
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=kicker.id, week=week, season=season
                    ).first()
                    if weekly_score:
                        total_points += weekly_score.fantasy_points
                        position_points['K'] = {
                            'player_id': kicker.id,
                            'points': weekly_score.fantasy_points
                        }
                
                if punter:
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=punter.id, week=week, season=season
                    ).first()
                    if weekly_score:
                        total_points += weekly_score.fantasy_points
                        position_points['P'] = {
                            'player_id': punter.id,
                            'points': weekly_score.fantasy_points
                        }
        
        # Update special teams lineup total
        special_lineup.special_teams_points = total_points
        db.session.commit()
        
        return {
            "success": True,
            "special_teams_points": total_points,
            "position_breakdown": position_points
        }

def calculate_team_score_modular(team_id, week, season):
    """Calculate total team score with modular breakdown"""
    with app.app_context():
        # Calculate points for each team type
        offense_result = calculate_offense_points(team_id, week, season)
        defense_result = calculate_defense_points(team_id, week, season)
        special_result = calculate_special_teams_points(team_id, week, season)
        
        # Check if any team type failed
        if not offense_result['success'] or not defense_result['success'] or not special_result['success']:
            return {
                "success": False,
                "message": "One or more team lineups not set",
                "offense_error": offense_result.get('message'),
                "defense_error": defense_result.get('message'),
                "special_error": special_result.get('message')
            }
        
        # Calculate totals
        offense_points = offense_result['offense_points']
        defense_points = defense_result['defense_points']
        special_points = special_result['special_teams_points']
        total_points = offense_points + defense_points + special_points
        
        return {
            "success": True,
            "offense_points": offense_points,
            "defense_points": defense_points,
            "special_teams_points": special_points,
            "total_points": total_points,
            "offense_breakdown": offense_result['position_breakdown'],
            "defense_breakdown": defense_result['position_breakdown'],
            "special_breakdown": special_result['position_breakdown']
        }

def get_cumulative_points(team_id, current_week, season):
    """Get cumulative points breakdown for all weeks up to current week"""
    with app.app_context():
        cumulative_data = []
        running_offense = 0.0
        running_defense = 0.0
        running_special = 0.0
        running_total = 0.0
        
        for week in range(1, current_week + 1):
            # Get points for this week
            offense_result = calculate_offense_points(team_id, week, season)
            defense_result = calculate_defense_points(team_id, week, season)
            special_result = calculate_special_teams_points(team_id, week, season)
            
            # Calculate week totals
            week_offense = offense_result['offense_points'] if offense_result['success'] else 0.0
            week_defense = defense_result['defense_points'] if defense_result['success'] else 0.0
            week_special = special_result['special_teams_points'] if special_result['success'] else 0.0
            week_total = week_offense + week_defense + week_special
            
            # Update running totals
            running_offense += week_offense
            running_defense += week_defense
            running_special += week_special
            running_total += week_total
            
            cumulative_data.append({
                'week': week,
                'offense_points': week_offense,
                'defense_points': week_defense,
                'special_teams_points': week_special,
                'week_total': week_total,
                'running_offense': running_offense,
                'running_defense': running_defense,
                'running_special': running_special,
                'running_total': running_total
            })
        
        return {
            "success": True,
            "team_id": team_id,
            "season": season,
            "current_week": current_week,
            "weekly_breakdown": cumulative_data,
            "final_totals": {
                "offense": running_offense,
                "defense": running_defense,
                "special_teams": running_special,
                "total": running_total
            }
        }

# =============================================================================
# MODULAR TEAM MANAGEMENT FUNCTIONS
# =============================================================================

def setup_offense_lineup(team_id, week, season, lineup_data):
    """Set up offense lineup for a specific week"""
    with app.app_context():
        try:
            # Delete existing lineup if any and commit the deletion first
            existing = OffenseLineup.query.filter_by(
                team_id=team_id, week=week, season=season
            ).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()  # Commit deletion first
            
            # Create new lineup
            lineup = OffenseLineup(
                team_id=team_id,
                week=week,
                season=season,
                qb_id=lineup_data.get('qb_id'),
                rb1_id=lineup_data.get('rb1_id'),
                rb2_id=lineup_data.get('rb2_id'),
                wr1_id=lineup_data.get('wr1_id'),
                wr2_id=lineup_data.get('wr2_id'),
                te_id=lineup_data.get('te_id')
            )
            
            db.session.add(lineup)
            db.session.commit()
            
            return {"success": True, "message": "Offense lineup set successfully"}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Error setting offense lineup: {e}"}

def setup_defense_lineup(team_id, week, season, lineup_data):
    """Set up defense lineup for a specific week"""
    with app.app_context():
        try:
            # Delete existing lineup if any and commit the deletion first
            existing = DefenseLineup.query.filter_by(
                team_id=team_id, week=week, season=season
            ).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()  # Commit deletion first
            
            # Create new lineup
            lineup = DefenseLineup(
                team_id=team_id,
                week=week,
                season=season,
                selection_type=lineup_data.get('selection_type', 'individual'),
                dl1_id=lineup_data.get('dl1_id'),
                dl2_id=lineup_data.get('dl2_id'),
                lb1_id=lineup_data.get('lb1_id'),
                lb2_id=lineup_data.get('lb2_id'),
                cb1_id=lineup_data.get('cb1_id'),
                cb2_id=lineup_data.get('cb2_id'),
                s1_id=lineup_data.get('s1_id'),
                s2_id=lineup_data.get('s2_id'),
                nfl_team_id=lineup_data.get('nfl_team_id')
            )
            
            db.session.add(lineup)
            db.session.commit()
            
            return {"success": True, "message": "Defense lineup set successfully"}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Error setting defense lineup: {e}"}

def setup_special_teams_lineup(team_id, week, season, lineup_data):
    """Set up special teams lineup for a specific week"""
    with app.app_context():
        try:
            # Delete existing lineup if any and commit the deletion first
            existing = SpecialTeamsLineup.query.filter_by(
                team_id=team_id, week=week, season=season
            ).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()  # Commit deletion first
            
            # Create new lineup
            lineup = SpecialTeamsLineup(
                team_id=team_id,
                week=week,
                season=season,
                selection_type=lineup_data.get('selection_type', 'individual'),
                kicker_id=lineup_data.get('kicker_id'),
                punter_id=lineup_data.get('punter_id'),
                nfl_team_id=lineup_data.get('nfl_team_id')
            )
            
            db.session.add(lineup)
            db.session.commit()
            
            return {"success": True, "message": "Special teams lineup set successfully"}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": f"Error setting special teams lineup: {e}"}
