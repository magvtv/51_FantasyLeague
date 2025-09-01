import click
from ..database import get_app, get_db
from ..models import NFLPlayer, WeeklyScore
from ..api_service import nfl_api
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import random

console = Console()

@click.group(name='data')
def data_commands():
    """Data management commands for NFL player data"""
    pass

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
@click.option('--weeks', type=int, default=5, help='Number of weeks to generate (default: 5)')
@click.option('--force', is_flag=True, help='Force regeneration even if data exists')
def generate_sample_scores(weeks, force):
    """Generate sample weekly scores for testing"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        console.print("Generating sample weekly scores...")
        
        # Get all players
        players = NFLPlayer.query.limit(50).all()
        
        if not players:
            console.print("No players found. Import players first with 'data import-nfl-data'", style="red")
            return
        
        generated_count = 0
        
        for week in range(1, weeks + 1):
            console.print(f"Generating scores for Week {week}...")
            
            for player in players:
                # Check if score already exists
                existing = WeeklyScore.query.filter_by(
                    player_id=player.id, week=week, season=2024
                ).first()
                
                if existing and not force:
                    continue
                
                # Generate realistic stats based on position
                stats = generate_sample_stats(player.position)
                fantasy_points = calculate_fantasy_points(stats)
                
                if existing:
                    # Update existing score
                    existing.passing_yards = stats['passing_yards']
                    existing.passing_tds = stats['passing_tds']
                    existing.passing_interceptions = stats['passing_interceptions']
                    existing.rushing_yards = stats['rushing_yards']
                    existing.rushing_tds = stats['rushing_tds']
                    existing.receiving_yards = stats['receiving_yards']
                    existing.receiving_tds = stats['receiving_tds']
                    existing.receptions = stats['receptions']
                    existing.fumbles = stats['fumbles']
                    existing.field_goals_made = stats['field_goals_made']
                    existing.extra_points_made = stats['extra_points_made']
                    existing.def_touchdowns = stats['def_touchdowns']
                    existing.def_interceptions = stats['def_interceptions']
                    existing.def_points_allowed = stats['def_points_allowed']
                    existing.fantasy_points = fantasy_points
                else:
                    # Create new score
                    weekly_score = WeeklyScore(
                        player_id=player.id,
                        week=week,
                        season=2024,
                        passing_yards=stats['passing_yards'],
                        passing_tds=stats['passing_tds'],
                        passing_interceptions=stats['passing_interceptions'],
                        rushing_yards=stats['rushing_yards'],
                        rushing_tds=stats['rushing_tds'],
                        receiving_yards=stats['receiving_yards'],
                        receiving_tds=stats['receiving_tds'],
                        receptions=stats['receptions'],
                        fumbles=stats['fumbles'],
                        field_goals_made=stats['field_goals_made'],
                        extra_points_made=stats['extra_points_made'],
                        def_touchdowns=stats['def_touchdowns'],
                        def_interceptions=stats['def_interceptions'],
                        def_points_allowed=stats['def_points_allowed'],
                        fantasy_points=fantasy_points
                    )
                    db.session.add(weekly_score)
                
                generated_count += 1
            
            db.session.commit()
        
        console.print(f"Generated {generated_count} weekly scores across {weeks} weeks")

def generate_sample_stats(position):
    """Generate realistic sample stats based on position"""
    stats = {
        'passing_yards': 0, 'passing_tds': 0, 'passing_interceptions': 0,
        'rushing_yards': 0, 'rushing_tds': 0,
        'receiving_yards': 0, 'receiving_tds': 0, 'receptions': 0,
        'fumbles': 0, 'field_goals_made': 0, 'extra_points_made': 0,
        'def_touchdowns': 0, 'def_interceptions': 0, 'def_points_allowed': 0
    }
    
    if position == 'QB':
        stats['passing_yards'] = random.randint(180, 350)
        stats['passing_tds'] = random.randint(0, 4)
        stats['passing_interceptions'] = random.randint(0, 2)
        stats['rushing_yards'] = random.randint(0, 50)
        stats['rushing_tds'] = random.randint(0, 1)
    elif position == 'RB':
        stats['rushing_yards'] = random.randint(40, 150)
        stats['rushing_tds'] = random.randint(0, 2)
        stats['receiving_yards'] = random.randint(10, 60)
        stats['receiving_tds'] = random.randint(0, 1)
        stats['receptions'] = random.randint(2, 8)
    elif position == 'WR':
        stats['receiving_yards'] = random.randint(30, 120)
        stats['receiving_tds'] = random.randint(0, 2)
        stats['receptions'] = random.randint(3, 10)
    elif position == 'TE':
        stats['receiving_yards'] = random.randint(20, 80)
        stats['receiving_tds'] = random.randint(0, 1)
        stats['receptions'] = random.randint(2, 7)
    elif position == 'K':
        stats['field_goals_made'] = random.randint(0, 4)
        stats['extra_points_made'] = random.randint(0, 5)
    elif position == 'DEF':
        stats['def_touchdowns'] = random.randint(0, 1)
        stats['def_interceptions'] = random.randint(0, 3)
        stats['def_points_allowed'] = random.randint(7, 35)
    
    # Random fumbles for skill positions
    if position in ['QB', 'RB', 'WR', 'TE']:
        stats['fumbles'] = random.randint(0, 1) if random.random() < 0.1 else 0
    
    return stats

def calculate_fantasy_points(stats):
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
