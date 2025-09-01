import click
from ..database import get_app, get_db
from ..models import User, FantasyTeam, NFLPlayer, TeamPlayer
from ..fantasy_logic import draft_player, transfer_player, get_team_summary
from ..api_service import nfl_api
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@click.group(name='team')
def team_commands():
    """Fantasy team management commands"""
    pass

@team_commands.command()
@click.option('--user-id', type=int, prompt='User ID', help='User ID who owns this team')
@click.option('--name', prompt='Team Name', help='Fantasy team name')
def create(user_id, name):
    """Create a new fantasy team"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            console.print("User not found", style="red")
            return
        
        # Check if team name already exists for this user
        existing_team = FantasyTeam.query.filter_by(user_id=user_id, name=name).first()
        if existing_team:
            console.print("You already have a team with that name", style="red")
            return
        
        try:
            team = FantasyTeam(
                name=name,
                user_id=user_id,
                budget_remaining=100000000,  # $100M starting budget
                free_transfers=1
            )
            
            db.session.add(team)
            db.session.commit()
            
            console.print(f"Team '{name}' created successfully!", style="green")
            console.print(f"Team ID: {team.id}")
            console.print(f"Starting Budget: $100,000,000")
            
        except Exception as e:
            console.print(f"Error creating team: {e}", style="red")
            db.session.rollback()

@team_commands.command()
@click.option('--team-id', type=int, help='Team ID to show')
@click.option('--user-id', type=int, help='Show all teams for this user')
def show(team_id, user_id):
    """Show team details"""
    app = get_app()
    
    with app.app_context():
        if team_id:
            summary = get_team_summary(team_id)
            if not summary:
                console.print("Team not found", style="red")
                return
            
            _display_team_summary(summary)
            
        elif user_id:
            teams = FantasyTeam.query.filter_by(user_id=user_id).all()
            if not teams:
                console.print("No teams found for this user", style="red")
                return
            
            for team in teams:
                summary = get_team_summary(team.id)
                if summary:
                    _display_team_summary(summary)
                    console.print()  # Empty line between teams
        else:
            console.print("Please provide either --team-id or --user-id", style="red")

def _display_team_summary(summary):
    """Helper function to display team summary"""
    # Team header
    console.print(Panel(
        f"[bold blue]{summary['team_name']}[/bold blue]\n" +
        f"Budget: ${summary['budget_remaining']:,.0f}\n" +
        f"Players: {summary['total_players']}/15\n" +
        f"Free Transfers: {summary['free_transfers']}",
        title="Team Summary"
    ))
    
    if summary['players']:
        # Group players by position
        positions = {}
        for player in summary['players']:
            pos = player['position']
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(player)
        
        # Display by position
        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            if position in positions:
                table = Table(title=f"{position} Players")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Team", style="blue")
                table.add_column("Price", style="green")
                table.add_column("Points", style="yellow")
                table.add_column("Status", style="red")
                
                for player in positions[position]:
                    status = "Injured" if player['is_injured'] else "Healthy"
                    table.add_row(
                        str(player['id']),
                        player['name'],
                        player['team'],
                        f"${player['price']:,.0f}",
                        f"{player['total_points']:.1f}",
                        status
                    )
                
                console.print(table)
                console.print()
    else:
        console.print("No players drafted yet. Use 'fantasy-cli team draft' to add players!")

@team_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--player-id', type=int, prompt='Player ID', help='Player ID to draft')
def draft(team_id, player_id):
    """Draft a player to your team"""
    result = draft_player(team_id, player_id)
    
    if result['success']:
        console.print(f"{result['message']}", style="green")
        console.print(f"Budget remaining: ${result['remaining_budget']:,.0f}")
    else:
        console.print(f"{result['message']}", style="red")

@team_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID')
@click.option('--player-out', type=int, prompt='Player ID to remove', help='Player to remove')
@click.option('--player-in', type=int, prompt='Player ID to add', help='Player to add')
@click.option('--week', type=int, prompt='Current week', help='Current gameweek')
@click.option('--season', type=int, default=2024, help='Season year')
def transfer(team_id, player_out, player_in, week, season):
    """Transfer a player (remove one, add another)"""
    result = transfer_player(team_id, player_out, player_in, week, season)
    
    if result['success']:
        console.print(f"{result['message']}", style="green")
        console.print(f"Budget remaining: ${result['remaining_budget']:,.0f}")
        console.print(f"Free transfers left: {result['free_transfers']}")
        if result['point_hit'] < 0:
            console.print(f"Point penalty: {result['point_hit']}", style="yellow")
    else:
        console.print(f"{result['message']}", style="red")

@team_commands.command()
@click.option('--position', help='Filter by position (QB, RB, WR, TE, K, DEF)')
@click.option('--team', help='Filter by NFL team')
@click.option('--max-price', type=int, help='Maximum price filter')
@click.option('--limit', type=int, default=20, help='Number of players to show')
def search(position, team, max_price, limit):
    """Search for available players to draft"""
    app = get_app()
    
    with app.app_context():
        query = NFLPlayer.query
        
        if position:
            query = query.filter(NFLPlayer.position == position.upper())
        if team:
            query = query.filter(NFLPlayer.team == team.upper())
        if max_price:
            query = query.filter(NFLPlayer.price <= max_price)
        
        players = query.order_by(NFLPlayer.total_points.desc()).limit(limit).all()
        
        if not players:
            console.print("No players found matching your criteria", style="red")
            return
        
        table = Table(title=f"Available Players ({len(players)} found)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Position", style="blue")
        table.add_column("Team", style="green")
        table.add_column("Price", style="yellow")
        table.add_column("Points", style="red")
        table.add_column("Status", style="white")
        
        for player in players:
            status = "Injured" if player.is_injured else "Healthy"
            table.add_row(
                str(player.id),
                player.name,
                player.position,
                player.team,
                f"${player.price:,.0f}",
                f"{player.total_points:.1f}",
                status
            )
        
        console.print(table)

@team_commands.command()
def list():
    """List all fantasy teams"""
    app = get_app()
    
    with app.app_context():
        teams = FantasyTeam.query.join(User).all()
        
        if not teams:
            console.print("No teams found", style="red")
            return
        
        table = Table(title="All Fantasy Teams")
        table.add_column("Team ID", style="cyan")
        table.add_column("Team Name", style="magenta")
        table.add_column("Owner", style="blue")
        table.add_column("Budget Left", style="green")
        table.add_column("Players", style="yellow")
        table.add_column("Total Points", style="red")
        
        for team in teams:
            player_count = len(team.team_players)
            table.add_row(
                str(team.id),
                team.name,
                team.owner.username,
                f"${team.budget_remaining:,.0f}",
                f"{player_count}/15",
                f"{team.total_points:.1f}"
            )
        
        console.print(table)

@team_commands.command()
@click.option('--team-id', type=int, prompt='Team ID', help='Team ID to delete')
@click.confirmation_option(prompt='Are you sure you want to delete this team?')
def delete(team_id):
    """Delete a fantasy team"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        team = FantasyTeam.query.get(team_id)
        if not team:
            console.print("Team not found", style="red")
            return
        
        try:
            team_name = team.name
            db.session.delete(team)
            db.session.commit()
            
            console.print(f"Team '{team_name}' deleted successfully!", style="green")
            
        except Exception as e:
            console.print(f"Error deleting team: {e}", style="red")
            db.session.rollback()
