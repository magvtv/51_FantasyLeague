import click
from ..database import get_app, get_db
from ..models import NFLPlayer, WeeklyScore
from ..api_service import nfl_api
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@click.group(name='data')
def data_commands():
    """Data management commands for NFL player data"""
    pass

@data_commands.command()
def list_commands():
    """List all available data management commands"""
    console.print("\n[bold]Available Data Management Commands:[/bold]")
    console.print("\n[cyan]1. import-nfl-data[/cyan]")
    console.print("   Import NFL player data from RapidAPI")
    console.print("   Options: --teams (number of teams), --force")
    
    console.print("\n[cyan]2. import-historical-scores[/cyan]")
    console.print("   Import historical weekly scores from 2024 season")
    console.print("   Options: --weeks (number of weeks), --season, --force")
    
    console.print("\n[cyan]3. import-season-stats[/cyan]")
    console.print("   Import season-long statistics for all players")
    console.print("   Options: --season, --force")
    
    console.print("\n[cyan]4. import-injury-data[/cyan]")
    console.print("   Import current injury data for all players")
    console.print("   Options: --force")
    
    console.print("\n[cyan]5. list-commands[/cyan]")
    console.print("   Show this help message")
    
    console.print("\n[bold]Usage Examples:[/bold]")
    console.print("  python cli.py data import-nfl-data --teams 10")
    console.print("  python cli.py data import-historical-scores --weeks 18 --season 2024")
    console.print("  python cli.py data import-season-stats --season 2024")
    console.print("  python cli.py data import-injury-data")

@data_commands.command()
@click.option('--teams', type=int, default=5, help='Number of teams to import (default: 5)')
@click.option('--force', is_flag=True, help='Force reimport even if data exists')
def import_nfl_data(teams, force):
    """Import NFL player data from RapidAPI"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        console.print("Importing NFL player data...")
        
        # Check if we have API key
        if not nfl_api.headers.get("x-rapidapi-key"):
            console.print("RAPIDAPI_KEY not found in environment variables", style="red")
            console.print("Please set RAPIDAPI_KEY in your .env file")
            return
        
        # Get teams data
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Fetching teams...", total=None)
            teams_data = nfl_api.get_team_data()
            progress.update(task, description="Teams fetched successfully")
        
        if not teams_data or 'teams' not in teams_data:
            console.print("Failed to fetch teams data", style="red")
            return
        
        teams_list = teams_data['teams'][:teams]  # Limit to specified number
        console.print(f"Found {len(teams_list)} teams to process")
        
        total_players = 0
        
        for team in teams_list:
            team_name = team.get('name', 'Unknown')
            team_abbr = team.get('abbreviation', 'UNK')
            
            console.print(f"\nProcessing {team_name} ({team_abbr})")
            
            # Get players for this team
            players_data = nfl_api.get_players_by_team(team.get('id'))
            
            if not players_data or 'players' not in players_data:
                console.print(f"No players found for {team_name}")
                continue
            
            players = players_data['players']
            imported_count = 0
            
            for player in players:
                try:
                    # Extract player data
                    nfl_id = player.get('id', f"{team_abbr}_{player.get('name', 'unknown')}")
                    name = player.get('name', 'Unknown Player')
                    position = player.get('position', 'UNKNOWN')
                    
                    # Calculate fantasy price based on position
                    base_prices = {
                        'QB': 8000000, 'RB': 7000000, 'WR': 6500000,
                        'TE': 5000000, 'K': 4000000, 'DEF': 4500000
                    }
                    price = base_prices.get(position, 5000000)
                    
                    # Check if player already exists
                    existing = NFLPlayer.query.filter_by(nfl_id=nfl_id).first()
                    if existing and not force:
                        continue
                    
                    # Create or update player
                    if existing:
                        existing.name = name
                        existing.position = position
                        existing.team = team_abbr
                        existing.price = price
                    else:
                        new_player = NFLPlayer(
                            nfl_id=nfl_id,
                            name=name,
                            position=position,
                            team=team_abbr,
                            price=price,
                            total_points=0.0,
                            is_injured=False
                        )
                        db.session.add(new_player)
                    
                    imported_count += 1
                    
                except Exception as e:
                    console.print(f"Error importing player {player.get('name', 'Unknown')}: {e}")
                    continue
            
            db.session.commit()
            total_players += imported_count
            console.print(f"Imported {imported_count} players for {team_name}")
        
        console.print(f"\nImport Summary:")
        console.print(f"Total players imported: {total_players}")
        console.print(f"Teams processed: {len(teams_list)}")

@data_commands.command()
@click.option('--weeks', type=int, default=18, help='Number of weeks to import (default: 18 for full season)')
@click.option('--season', type=int, default=2024, help='Season to import data for (default: 2024)')
@click.option('--force', is_flag=True, help='Force reimport even if data exists')
def import_historical_scores(weeks, season, force):
    """Import historical weekly scores from RapidAPI for 2024 season"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        console.print(f"Importing historical scores for {season} season...")
        
        # Check if we have API key
        if not nfl_api.headers.get("x-rapidapi-key"):
            console.print("RAPIDAPI_KEY not found in environment variables", style="red")
            console.print("Please set RAPIDAPI_KEY in your .env file")
            return
        
        # Get all players from database
        players = NFLPlayer.query.all()
        
        if not players:
            console.print("No players found in database. Import players first with 'data import-nfl-data'", style="red")
            return
        
        console.print(f"Found {len(players)} players in database")
        
        total_scores_imported = 0
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            for week in range(1, weeks + 1):
                task = progress.add_task(f"Processing Week {week}...", total=len(players))
                
                # Get weekly stats from API
                weekly_stats = nfl_api.get_weekly_stats(season, week)
                
                if not weekly_stats or 'players' not in weekly_stats:
                    console.print(f"No stats found for Week {week} Season {season}", style="yellow")
                    continue
                
                week_scores_imported = 0
                
                for player in players:
                    progress.update(task, advance=1)
                    
                    # Find player stats in the weekly data
                    player_stats = None
                    for stat_entry in weekly_stats['players']:
                        if isinstance(stat_entry, dict):
                            if stat_entry.get('playerId') == player.nfl_id or stat_entry.get('player', {}).get('id') == player.nfl_id:
                                player_stats = stat_entry
                                break
                    
                    if not player_stats:
                        continue
                    
                    # Check if score already exists
                    existing = WeeklyScore.query.filter_by(
                        player_id=player.id, week=week, season=season
                    ).first()
                    
                    if existing and not force:
                        continue
                    
                    # Extract stats from API response
                    stats = extract_stats_from_api(player_stats, player.position)
                    fantasy_points = calculate_fantasy_points_from_stats(stats)
                    
                    if existing:
                        # Update existing score
                        update_weekly_score(existing, stats, fantasy_points)
                    else:
                        # Create new score
                        weekly_score = WeeklyScore(
                            player_id=player.id,
                            week=week,
                            season=season,
                            **stats,
                            fantasy_points=fantasy_points
                        )
                        db.session.add(weekly_score)
                    
                    week_scores_imported += 1
                
                db.session.commit()
                total_scores_imported += week_scores_imported
                console.print(f"Week {week}: Imported {week_scores_imported} scores")
        
        console.print(f"\nImport Summary:")
        console.print(f"Total scores imported: {total_scores_imported}")
        console.print(f"Weeks processed: {weeks}")
        console.print(f"Season: {season}")

@data_commands.command()
@click.option('--season', type=int, default=2024, help='Season to import data for (default: 2024)')
@click.option('--force', is_flag=True, help='Force reimport even if data exists')
def import_season_stats(season, force):
    """Import season-long statistics for all players"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        console.print(f"Importing season stats for {season} season...")
        
        # Check if we have API key
        if not nfl_api.headers.get("x-rapidapi-key"):
            console.print("RAPIDAPI_KEY not found in environment variables", style="red")
            console.print("Please set RAPIDAPI_KEY in your .env file")
            return
        
        # Get all players from database
        players = NFLPlayer.query.all()
        
        if not players:
            console.print("No players found in database. Import players first with 'data import-nfl-data'", style="red")
            return
        
        console.print(f"Found {len(players)} players in database")
        
        # Get season stats from API
        season_stats = nfl_api.get_season_stats(season)
        
        if not season_stats or 'players' not in season_stats:
            console.print(f"No season stats found for {season}", style="red")
            return
        
        updated_count = 0
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Processing season stats...", total=len(players))
            
            for player in players:
                progress.update(task, advance=1)
                
                # Find player stats in the season data
                player_stats = None
                for stat_entry in season_stats['players']:
                    if isinstance(stat_entry, dict):
                        if stat_entry.get('playerId') == player.nfl_id or stat_entry.get('player', {}).get('id') == player.nfl_id:
                            player_stats = stat_entry
                            break
                
                if not player_stats:
                    continue
                
                # Calculate total fantasy points for the season
                stats = extract_stats_from_api(player_stats, player.position)
                total_fantasy_points = calculate_fantasy_points_from_stats(stats)
                
                # Update player's total points
                if force or player.total_points == 0.0:
                    player.total_points = total_fantasy_points
                    updated_count += 1
        
        db.session.commit()
        console.print(f"Updated total points for {updated_count} players")

@data_commands.command()
@click.option('--force', is_flag=True, help='Force reimport even if data exists')
def import_injury_data(force):
    """Import current injury data for all players"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        console.print("Importing injury data...")
        
        # Check if we have API key
        if not nfl_api.headers.get("x-rapidapi-key"):
            console.print("RAPIDAPI_KEY not found in environment variables", style="red")
            console.print("Please set RAPIDAPI_KEY in your .env file")
            return
        
        # Get all players from database
        players = NFLPlayer.query.all()
        
        if not players:
            console.print("No players found in database. Import players first with 'data import-nfl-data'", style="red")
            return
        
        console.print(f"Found {len(players)} players in database")
        
        # Get injury report from API
        injury_report = nfl_api.get_injury_report()
        
        if not injury_report:
            console.print("No injury report found", style="red")
            return
        
        updated_count = 0
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Processing injury data...", total=len(players))
            
            for player in players:
                progress.update(task, advance=1)
                
                # Find player in injury report
                player_injury = None
                for injury_entry in injury_report:
                    if isinstance(injury_entry, dict):
                        if injury_entry.get('playerId') == player.nfl_id or injury_entry.get('player', {}).get('id') == player.nfl_id:
                            player_injury = injury_entry
                            break
                
                if player_injury:
                    # Update player injury status
                    injury_status = player_injury.get('status', 'Unknown')
                    is_injured = injury_status.lower() in ['out', 'doubtful', 'questionable']
                    
                    if force or player.injury_status != injury_status:
                        player.is_injured = is_injured
                        player.injury_status = injury_status
                        updated_count += 1
                else:
                    # Player not in injury report, mark as healthy
                    if force or player.is_injured:
                        player.is_injured = False
                        player.injury_status = 'Healthy'
                        updated_count += 1
        
        db.session.commit()
        console.print(f"Updated injury status for {updated_count} players")

def extract_stats_from_api(player_stats, position):
    """Extract relevant stats from API response based on position"""
    stats = {
        'passing_yards': 0.0, 'passing_tds': 0, 'passing_interceptions': 0,
        'rushing_yards': 0.0, 'rushing_tds': 0,
        'receiving_yards': 0.0, 'receiving_tds': 0, 'receptions': 0,
        'fumbles': 0, 'field_goals_made': 0, 'extra_points_made': 0,
        'def_touchdowns': 0, 'def_interceptions': 0, 'def_points_allowed': 0
    }
    
    # Extract stats based on position
    if position == 'QB':
        stats.update({
            'passing_yards': float(player_stats.get('passingYards', 0)),
            'passing_tds': int(player_stats.get('passingTouchdowns', 0)),
            'passing_interceptions': int(player_stats.get('passingInterceptions', 0)),
            'rushing_yards': float(player_stats.get('rushingYards', 0)),
            'rushing_tds': int(player_stats.get('rushingTouchdowns', 0)),
            'fumbles': int(player_stats.get('fumbles', 0))
        })
    elif position == 'RB':
        stats.update({
            'rushing_yards': float(player_stats.get('rushingYards', 0)),
            'rushing_tds': int(player_stats.get('rushingTouchdowns', 0)),
            'receiving_yards': float(player_stats.get('receivingYards', 0)),
            'receiving_tds': int(player_stats.get('receivingTouchdowns', 0)),
            'receptions': int(player_stats.get('receptions', 0)),
            'fumbles': int(player_stats.get('fumbles', 0))
        })
    elif position == 'WR':
        stats.update({
            'receiving_yards': float(player_stats.get('receivingYards', 0)),
            'receiving_tds': int(player_stats.get('receivingTouchdowns', 0)),
            'receptions': int(player_stats.get('receptions', 0)),
            'fumbles': int(player_stats.get('fumbles', 0))
        })
    elif position == 'TE':
        stats.update({
            'receiving_yards': float(player_stats.get('receivingYards', 0)),
            'receiving_tds': int(player_stats.get('receivingTouchdowns', 0)),
            'receptions': int(player_stats.get('receptions', 0)),
            'fumbles': int(player_stats.get('fumbles', 0))
        })
    elif position == 'K':
        stats.update({
            'field_goals_made': int(player_stats.get('fieldGoalsMade', 0)),
            'extra_points_made': int(player_stats.get('extraPointsMade', 0))
        })
    elif position == 'DEF':
        stats.update({
            'def_touchdowns': int(player_stats.get('defensiveTouchdowns', 0)),
            'def_interceptions': int(player_stats.get('interceptions', 0)),
            'def_points_allowed': int(player_stats.get('pointsAllowed', 0))
        })
    
    return stats

def calculate_fantasy_points_from_stats(stats):
    """Calculate fantasy points from stats (PPR scoring)"""
    points = 0.0
    
    # Passing
    points += (stats['passing_yards'] / 25) * 1
    points += stats['passing_tds'] * 4
    points -= stats['passing_interceptions'] * 2
    
    # Rushing
    points += (stats['rushing_yards'] / 10) * 1
    points += stats['rushing_tds'] * 6
    
    # Receiving
    points += (stats['receiving_yards'] / 10) * 1
    points += stats['receiving_tds'] * 6
    points += stats['receptions'] * 1  # PPR
    
    # Fumbles
    points -= stats['fumbles'] * 2
    
    # Kicking
    points += stats['field_goals_made'] * 3
    points += stats['extra_points_made'] * 1
    
    # Defense
    points += stats['def_touchdowns'] * 6
    points += stats['def_interceptions'] * 2
    
    # Points allowed by defense
    points_allowed = stats['def_points_allowed']
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

def update_weekly_score(existing_score, stats, fantasy_points):
    """Update existing weekly score with new stats"""
    existing_score.passing_yards = stats['passing_yards']
    existing_score.passing_tds = stats['passing_tds']
    existing_score.passing_interceptions = stats['passing_interceptions']
    existing_score.rushing_yards = stats['rushing_yards']
    existing_score.rushing_tds = stats['rushing_tds']
    existing_score.receiving_yards = stats['receiving_yards']
    existing_score.receiving_tds = stats['receiving_tds']
    existing_score.receptions = stats['receptions']
    existing_score.fumbles = stats['fumbles']
    existing_score.field_goals_made = stats['field_goals_made']
    existing_score.extra_points_made = stats['extra_points_made']
    existing_score.def_touchdowns = stats['def_touchdowns']
    existing_score.def_interceptions = stats['def_interceptions']
    existing_score.def_points_allowed = stats['def_points_allowed']
    existing_score.fantasy_points = fantasy_points
