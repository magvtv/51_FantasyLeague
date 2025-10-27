import click
from ..database import get_app, get_db
from ..models import (
    FantasyTeam, WeeklyLineup, WeeklyScore, NFLPlayer, TeamPlayer, User,
    OffenseLineup, DefenseLineup, SpecialTeamsLineup, NFLTeam
)
from ..fantasy_logic import (
    calculate_team_score, validate_lineup, calculate_team_score_modular,
    calculate_offense_points, calculate_defense_points, calculate_special_teams_points,
    get_cumulative_points, setup_offense_lineup, setup_defense_lineup, setup_special_teams_lineup
)
from ..api_service import nfl_api
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@click.group(name='gameweek')
def gameweek_commands():
    """Gameweek and lineup management commands"""
    pass

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
def setup(team_id, week, season):
    """Set up lineup for a gameweek"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        if not team:
            console.print("Team not found", style="red")
            return
        
        # Get team players grouped by position
        team_players = db.session.query(TeamPlayer, NFLPlayer).join(
            NFLPlayer, TeamPlayer.player_id == NFLPlayer.id
        ).filter(TeamPlayer.team_id == team_id).all()
        
        if not team_players:
            console.print("No players in team. Draft some players first!", style="red")
            return
        
        # Group by position
        positions = {}
        for team_player, nfl_player in team_players:
            pos = nfl_player.position
            if pos not in positions:
                positions[pos] = []
            positions[pos].append((team_player, nfl_player))
        
        console.print(f"\nSetting up lineup for Week {week}, {season}")
        console.print(f"Team: {team.name}\n")
        
        lineup_data = {}
        
        # Required positions and their limits
        position_setup = [
            ('QB', 'qb_id', 1, 'Quarterback'),
            ('RB', 'rb1_id', 1, 'Running Back 1'),
            ('RB', 'rb2_id', 1, 'Running Back 2'),
            ('WR', 'wr1_id', 1, 'Wide Receiver 1'),
            ('WR', 'wr2_id', 1, 'Wide Receiver 2'),
            ('TE', 'te_id', 1, 'Tight End'),
            ('K', 'k_id', 1, 'Kicker'),
            ('DEF', 'def_id', 1, 'Defense')
        ]
        
        for pos_code, field_name, count, display_name in position_setup:
            if pos_code in positions:
                players = positions[pos_code]
                
                console.print(f"\nSelect {display_name}:")
                table = Table()
                table.add_column("Option", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Team", style="blue")
                table.add_column("Points", style="yellow")
                table.add_column("Status", style="green")
                
                for i, (team_player, nfl_player) in enumerate(players, 1):
                    status = "Injured" if nfl_player.is_injured else "Healthy"
                    table.add_row(
                        str(i),
                        nfl_player.name,
                        nfl_player.team,
                        f"{nfl_player.total_points:.1f}",
                        status
                    )
                
                console.print(table)
                
                while True:
                    try:
                        choice = click.prompt(f"Select {display_name} (1-{len(players)})", type=int)
                        if 1 <= choice <= len(players):
                            selected_player = players[choice-1][1]
                            lineup_data[field_name] = selected_player.id
                            console.print(f"Selected: {selected_player.name}")
                            break
                        else:
                            console.print("Invalid choice, try again")
                    except (ValueError, click.Abort):
                        console.print("Invalid input, try again")
            else:
                console.print(f"No {display_name} available in your team!", style="red")
                return
        
        # Validate lineup
        validation = validate_lineup(team_id, lineup_data)
        if not validation['valid']:
            console.print(f"Lineup validation failed: {validation['message']}", style="red")
            return
        
        # Save lineup
        try:
            # Delete existing lineup if any
            existing = WeeklyLineup.query.filter_by(
                team_id=team_id, week=week, season=season
            ).first()
            if existing:
                db.session.delete(existing)
            
            # Create new lineup
            lineup = WeeklyLineup(
                team_id=team_id,
                week=week,
                season=season,
                **lineup_data
            )
            
            db.session.add(lineup)
            db.session.commit()
            
            console.print(f"\nLineup for Week {week} saved successfully!", style="green")
            
            # Show final lineup
            _display_lineup(lineup)
            
        except Exception as e:
            console.print(f"Error saving lineup: {e}", style="red")
            db.session.rollback()

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
def lineup(team_id, week, season):
    """Show lineup for a specific gameweek"""
    app = get_app()
    
    with app.app_context():
        lineup = WeeklyLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if not lineup:
            console.print(f"No lineup set for Week {week}", style="red")
            console.print("Use 'fantasy-cli gameweek setup' to create a lineup")
            return
        
        team = FantasyTeam.query.get(team_id)
        console.print(f"\nLineup for {team.name} - Week {week}, {season}")
        
        _display_lineup(lineup)

def _display_lineup(lineup):
    """Helper function to display lineup"""
    app = get_app()
    
    with app.app_context():
        positions = [
            ('QB', lineup.qb_id),
            ('RB1', lineup.rb1_id),
            ('RB2', lineup.rb2_id),
            ('WR1', lineup.wr1_id),
            ('WR2', lineup.wr2_id),
            ('TE', lineup.te_id),
            ('K', lineup.k_id),
            ('DEF', lineup.def_id)
        ]
        
        table = Table(title="Starting Lineup")
        table.add_column("Position", style="cyan")
        table.add_column("Player", style="magenta")
        table.add_column("Team", style="blue")
        table.add_column("Points", style="yellow")
        table.add_column("Status", style="green")
        
        total_points = 0
        for pos_name, player_id in positions:
            if player_id:
                player = NFLPlayer.query.get(player_id)
                if player:
                    # Get weekly score if available
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=player_id, 
                        week=lineup.week, 
                        season=lineup.season
                    ).first()
                    
                    points = weekly_score.fantasy_points if weekly_score else 0.0
                    total_points += points
                    
                    status = "Injured" if player.is_injured else "Healthy"
                    table.add_row(
                        pos_name,
                        player.name,
                        player.team,
                        f"{points:.1f}",
                        status
                    )
        
        console.print(table)
        console.print(f"\nTotal Points: {total_points:.1f}")

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
def calculate(team_id, week, season):
    """Calculate points for a gameweek"""
    result = calculate_team_score(team_id, week, season)
    
    if result['success']:
        console.print(f"Points calculated for Week {week}", style="green")
        console.print(f"Total Points: {result['total_points']:.1f}")
        
        if result.get('position_breakdown'):
            table = Table(title="Points Breakdown")
            table.add_column("Position", style="cyan")
            table.add_column("Points", style="yellow")
            
            for pos, data in result['position_breakdown'].items():
                table.add_row(pos, f"{data['points']:.1f}")
            
            console.print(table)
    else:
        console.print(f"{result['message']}", style="red")

@gameweek_commands.command()
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
def leaderboard(week, season):
    """Show leaderboard for a specific gameweek"""
    app = get_app()
    
    with app.app_context():
        # Get all lineups for the week
        db = get_db()
        lineups = db.session.query(WeeklyLineup, FantasyTeam, User).join(
            FantasyTeam, WeeklyLineup.team_id == FantasyTeam.id
        ).join(
            User, FantasyTeam.user_id == User.id
        ).filter(
            WeeklyLineup.week == week,
            WeeklyLineup.season == season
        ).order_by(WeeklyLineup.total_points.desc()).all()
        
        if not lineups:
            console.print(f"No lineups found for Week {week}", style="red")
            return
        
        table = Table(title=f"Week {week} Leaderboard")
        table.add_column("Rank", style="cyan")
        table.add_column("Team", style="magenta")
        table.add_column("Owner", style="blue")
        table.add_column("Points", style="yellow")
        table.add_column("Status", style="green")
        
        for i, (lineup, team, user) in enumerate(lineups, 1):
            status = "Complete" if lineup.is_finalized else "Pending"
            table.add_row(
                str(i),
                team.name,
                user.username,
                f"{lineup.total_points:.1f}",
                status
            )
        
        console.print(table)

@gameweek_commands.command()
@click.option('--week', type=int, help='Specific week to show')
@click.option('--season', type=int, default=2024, help='Season year')
def fixtures(week, season):
    """Show NFL fixtures/games for the week"""
    try:
        if week:
            games = nfl_api.get_games_by_week(season, week)
        else:
            # Show current week or upcoming games
            console.print("Fetching current NFL fixtures...")
            games = nfl_api.get_live_scores()
        
        if not games:
            console.print("No games found", style="red")
            return
        
        console.print(f"NFL Fixtures - Week {week if week else 'Current'}")
        
        # This would need to be adapted based on actual API response format
        console.print("Game data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
        
    except Exception as e:
        console.print(f"Error fetching fixtures: {e}", style="red")

# =============================================================================
# MODULAR TEAM COMMANDS
# =============================================================================

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
def setup_offense(team_id, week, season):
    """Set up offense lineup for a gameweek"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        console.print(f"Looking for team ID: {team_id}", style="blue")
        team = FantasyTeam.query.get(team_id)
        console.print(f"Team query result: {team}", style="blue")
        if not team:
            console.print("Team not found", style="red")
            return
        
        # Get team players grouped by offensive position
        team_players = db.session.query(TeamPlayer, NFLPlayer).join(
            NFLPlayer, TeamPlayer.player_id == NFLPlayer.id
        ).filter(
            TeamPlayer.team_id == team_id,
            NFLPlayer.position.in_(['QB', 'RB', 'WR', 'TE'])
        ).all()
        
        if not team_players:
            console.print("No offensive players in team. Draft some players first!", style="red")
            return
        
        # Group by position
        positions = {}
        for team_player, nfl_player in team_players:
            pos = nfl_player.position
            if pos not in positions:
                positions[pos] = []
            positions[pos].append((team_player, nfl_player))
        
        console.print(f"\nSetting up OFFENSE lineup for Week {week}, {season}")
        console.print(f"Team: {team.name}\n")
        
        lineup_data = {}
        
        # Required offensive positions
        position_setup = [
            ('QB', 'qb_id', 'Quarterback'),
            ('RB', 'rb1_id', 'Running Back 1'),
            ('RB', 'rb2_id', 'Running Back 2'),
            ('WR', 'wr1_id', 'Wide Receiver 1'),
            ('WR', 'wr2_id', 'Wide Receiver 2'),
            ('TE', 'te_id', 'Tight End')
        ]
        
        for pos_code, field_name, display_name in position_setup:
            if pos_code in positions:
                players = positions[pos_code]
                
                console.print(f"\nSelect {display_name}:")
                table = Table()
                table.add_column("Option", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Team", style="blue")
                table.add_column("Points", style="yellow")
                table.add_column("Status", style="green")
                
                for i, (team_player, nfl_player) in enumerate(players, 1):
                    status = "Injured" if nfl_player.is_injured else "Healthy"
                    table.add_row(
                        str(i),
                        nfl_player.name,
                        nfl_player.team,
                        f"{nfl_player.total_points:.1f}",
                        status
                    )
                
                console.print(table)
                
                while True:
                    try:
                        choice = click.prompt(f"Select {display_name} (1-{len(players)})", type=int)
                        if 1 <= choice <= len(players):
                            selected_player = players[choice-1][1]
                            lineup_data[field_name] = selected_player.id
                            console.print(f"Selected: {selected_player.name}")
                            break
                        else:
                            console.print("Invalid choice, try again")
                    except (ValueError, click.Abort):
                        console.print("Invalid input, try again")
            else:
                console.print(f"No {display_name} available in your team!", style="red")
                return
        
        # Save offense lineup
        result = setup_offense_lineup(team_id, week, season, lineup_data)
        
        if result['success']:
            console.print(f"\nOffense lineup for Week {week} saved successfully!", style="green")
        else:
            console.print(f"Error saving offense lineup: {result['message']}", style="red")

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
@click.option('--nfl-team', help='NFL team code (e.g., TB, KC) for team selection')
def setup_defense(team_id, week, season, nfl_team):
    """Set up defense lineup for a gameweek"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        if not team:
            console.print("Team not found", style="red")
            return
        
        console.print(f"\nSetting up DEFENSE lineup for Week {week}, {season}")
        console.print(f"Team: {team.name}\n")
        
        lineup_data = {}
        
        if nfl_team:
            # Team selection mode
            nfl_team_obj = NFLTeam.query.filter_by(team_code=nfl_team.upper()).first()
            if not nfl_team_obj:
                console.print(f"NFL team '{nfl_team}' not found", style="red")
                return
            
            lineup_data = {
                'selection_type': 'team',
                'nfl_team_id': nfl_team_obj.id
            }
            
            console.print(f"Selected {nfl_team_obj.team_name} defense", style="green")
        
        else:
            # Individual player selection mode
            console.print("Individual player selection not implemented yet.", style="yellow")
            console.print("Use --nfl-team option to select entire team defense.", style="yellow")
            return
        
        # Save defense lineup
        result = setup_defense_lineup(team_id, week, season, lineup_data)
        
        if result['success']:
            console.print(f"\nDefense lineup for Week {week} saved successfully!", style="green")
        else:
            console.print(f"Error saving defense lineup: {result['message']}", style="red")

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
@click.option('--nfl-team', help='NFL team code (e.g., TB, KC) for team selection')
def setup_special(team_id, week, season, nfl_team):
    """Set up special teams lineup for a gameweek"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        if not team:
            console.print("Team not found", style="red")
            return
        
        console.print(f"\nSetting up SPECIAL TEAMS lineup for Week {week}, {season}")
        console.print(f"Team: {team.name}\n")
        
        lineup_data = {}
        
        if nfl_team:
            # Team selection mode
            nfl_team_obj = NFLTeam.query.filter_by(team_code=nfl_team.upper()).first()
            if not nfl_team_obj:
                console.print(f"NFL team '{nfl_team}' not found", style="red")
                return
            
            lineup_data = {
                'selection_type': 'team',
                'nfl_team_id': nfl_team_obj.id
            }
            
            console.print(f"Selected {nfl_team_obj.team_name} special teams", style="green")
        
        else:
            # Individual player selection mode
            console.print("Individual player selection not implemented yet.", style="yellow")
            console.print("Use --nfl-team option to select entire team special teams.", style="yellow")
            return
        
        # Save special teams lineup
        result = setup_special_teams_lineup(team_id, week, season, lineup_data)
        
        if result['success']:
            console.print(f"\nSpecial teams lineup for Week {week} saved successfully!", style="green")
        else:
            console.print(f"Error saving special teams lineup: {result['message']}", style="red")

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Week number', help='Gameweek number')
@click.option('--season', type=int, default=2024, help='Season year')
def view_modular(team_id, week, season):
    """View modular lineup breakdown for a specific gameweek"""
    app = get_app()
    
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        if not team:
            console.print("Team not found", style="red")
            return
        
        console.print(f"\nModular Lineup for {team.name} - Week {week}, {season}")
        console.print("=" * 60)
        
        # Get offense lineup
        offense_lineup = OffenseLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if offense_lineup:
            console.print("\n[bold blue]OFFENSE[/bold blue]")
            _display_offense_lineup(offense_lineup, week, season)
        else:
            console.print("\n[bold red]OFFENSE[/bold red] - No lineup set")
        
        # Get defense lineup
        defense_lineup = DefenseLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if defense_lineup:
            console.print("\n[bold green]DEFENSE[/bold green]")
            _display_defense_lineup(defense_lineup, week, season)
        else:
            console.print("\n[bold red]DEFENSE[/bold red] - No lineup set")
        
        # Get special teams lineup
        special_lineup = SpecialTeamsLineup.query.filter_by(
            team_id=team_id, week=week, season=season
        ).first()
        
        if special_lineup:
            console.print("\n[bold yellow]SPECIAL TEAMS[/bold yellow]")
            _display_special_teams_lineup(special_lineup, week, season)
        else:
            console.print("\n[bold red]SPECIAL TEAMS[/bold red] - No lineup set")
        
        # Calculate and display totals
        result = calculate_team_score_modular(team_id, week, season)
        if result['success']:
            console.print(f"\n[bold]TOTAL POINTS: {result['total_points']:.1f}[/bold]")
            console.print(f"Offense: {result['offense_points']:.1f} | Defense: {result['defense_points']:.1f} | Special Teams: {result['special_teams_points']:.1f}")

@gameweek_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--week', type=int, prompt='Current week', help='Current gameweek')
@click.option('--season', type=int, default=2024, help='Season year')
def cumulative(team_id, week, season):
    """View cumulative points breakdown for all weeks up to current week"""
    app = get_app()
    
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        if not team:
            console.print("Team not found", style="red")
            return
        
        console.print(f"\nCumulative Points for {team.name} - Through Week {week}, {season}")
        console.print("=" * 80)
        
        result = get_cumulative_points(team_id, week, season)
        
        if not result['success']:
            console.print(f"Error: {result.get('message', 'Unknown error')}", style="red")
            return
        
        # Create cumulative table
        table = Table(title=f"Weekly Breakdown - {team.name}")
        table.add_column("Week", style="cyan")
        table.add_column("Offense", style="blue")
        table.add_column("Defense", style="green")
        table.add_column("Special", style="yellow")
        table.add_column("Total", style="bold")
        table.add_column("Running Total", style="bold red")
        
        for week_data in result['weekly_breakdown']:
            table.add_row(
                str(week_data['week']),
                f"{week_data['offense_points']:.1f}",
                f"{week_data['defense_points']:.1f}",
                f"{week_data['special_teams_points']:.1f}",
                f"{week_data['week_total']:.1f}",
                f"{week_data['running_total']:.1f}"
            )
        
        console.print(table)
        
        # Display final totals
        final_totals = result['final_totals']
        console.print(f"\n[bold]FINAL TOTALS:[/bold]")
        console.print(f"Offense: {final_totals['offense']:.1f}")
        console.print(f"Defense: {final_totals['defense']:.1f}")
        console.print(f"Special Teams: {final_totals['special_teams']:.1f}")
        console.print(f"[bold]GRAND TOTAL: {final_totals['total']:.1f}[/bold]")

# =============================================================================
# HELPER FUNCTIONS FOR DISPLAY
# =============================================================================

def _display_offense_lineup(lineup, week, season):
    """Helper function to display offense lineup"""
    app = get_app()
    
    with app.app_context():
        positions = [
            ('QB', lineup.qb_id),
            ('RB1', lineup.rb1_id),
            ('RB2', lineup.rb2_id),
            ('WR1', lineup.wr1_id),
            ('WR2', lineup.wr2_id),
            ('TE', lineup.te_id)
        ]
        
        table = Table()
        table.add_column("Position", style="cyan")
        table.add_column("Player", style="magenta")
        table.add_column("Team", style="blue")
        table.add_column("Points", style="yellow")
        
        total_points = 0
        for pos_name, player_id in positions:
            if player_id:
                player = NFLPlayer.query.get(player_id)
                if player:
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=player_id, week=week, season=season
                    ).first()
                    
                    points = weekly_score.fantasy_points if weekly_score else 0.0
                    total_points += points
                    
                    table.add_row(
                        pos_name,
                        player.name,
                        player.team,
                        f"{points:.1f}"
                    )
        
        console.print(table)
        console.print(f"Offense Total: {total_points:.1f}")

def _display_defense_lineup(lineup, week, season):
    """Helper function to display defense lineup"""
    app = get_app()
    
    with app.app_context():
        if lineup.selection_type == 'team':
            nfl_team = NFLTeam.query.get(lineup.nfl_team_id)
            if nfl_team:
                console.print(f"Team Defense: {nfl_team.team_name}")
                
                # Get team defense player
                team_def_player = NFLPlayer.query.filter_by(
                    team=nfl_team.team_code, position='DEF'
                ).first()
                
                if team_def_player:
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=team_def_player.id, week=week, season=season
                    ).first()
                    
                    points = weekly_score.fantasy_points if weekly_score else 0.0
                    console.print(f"Defense Points: {points:.1f}")
        else:
            console.print("Individual player defense (not implemented)")

def _display_special_teams_lineup(lineup, week, season):
    """Helper function to display special teams lineup"""
    app = get_app()
    
    with app.app_context():
        if lineup.selection_type == 'team':
            nfl_team = NFLTeam.query.get(lineup.nfl_team_id)
            if nfl_team:
                console.print(f"Team Special Teams: {nfl_team.team_name}")
                
                # Get special teams players
                kicker = NFLPlayer.query.filter_by(
                    team=nfl_team.team_code, position='K'
                ).first()
                punter = NFLPlayer.query.filter_by(
                    team=nfl_team.team_code, position='P'
                ).first()
                
                total_points = 0
                if kicker:
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=kicker.id, week=week, season=season
                    ).first()
                    points = weekly_score.fantasy_points if weekly_score else 0.0
                    total_points += points
                    console.print(f"Kicker ({kicker.name}): {points:.1f}")
                
                if punter:
                    weekly_score = WeeklyScore.query.filter_by(
                        player_id=punter.id, week=week, season=season
                    ).first()
                    points = weekly_score.fantasy_points if weekly_score else 0.0
                    total_points += points
                    console.print(f"Punter ({punter.name}): {points:.1f}")
                
                console.print(f"Special Teams Total: {total_points:.1f}")
        else:
            console.print("Individual player special teams (not implemented)")
