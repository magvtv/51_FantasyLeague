import click
from ..database import get_app, get_db
from ..models import User, FantasyTeam
from rich.console import Console
from rich.table import Table

console = Console()

@click.group(name='user')
def user_commands():
    """User management commands"""
    pass

@user_commands.command()
@click.option('--username', prompt='Username', help='Your username')
@click.option('--email', prompt='Email', help='Your email address')
def register(username, email):
    """Register a new user"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            console.print("User with that username or email already exists!", style="red")
            return
        
        # Create new user
        try:
            new_user = User(username=username, email=email)
            db.session.add(new_user)
            db.session.commit()
            
            console.print(f"User '{username}' registered successfully!", style="green")
            console.print(f"User ID: {new_user.id}")
            
        except Exception as e:
            console.print(f"Error creating user: {e}", style="red")
            db.session.rollback()

@user_commands.command()
def list():
    """List all registered users"""
    app = get_app()
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            console.print("No users registered yet.", style="yellow")
            return
        
        table = Table(title="Registered Users")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Username", style="magenta")
        table.add_column("Email", style="green")
        table.add_column("Teams", style="blue")
        table.add_column("Created", style="yellow")
        
        for user in users:
            team_count = len(user.fantasy_teams)
            table.add_row(
                str(user.id),
                user.username,
                user.email,
                str(team_count),
                user.created_at.strftime("%Y-%m-%d")
            )
        
        console.print(table)

@user_commands.command()
@click.option('--user-id', type=int, help='User ID to show profile for')
@click.option('--username', help='Username to show profile for')
def profile(user_id, username):
    """Show user profile and teams"""
    app = get_app()
    
    with app.app_context():
        if user_id:
            user = User.query.get(user_id)
        elif username:
            user = User.query.filter_by(username=username).first()
        else:
            console.print("Please provide either --user-id or --username", style="red")
            return
        
        if not user:
            console.print("User not found", style="red")
            return
        
        # User info
        console.print(f"\n[bold blue]{user.username}[/bold blue]")
        console.print(f"Email: {user.email}")
        console.print(f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Teams
        teams = user.fantasy_teams
        if teams:
            console.print(f"\nFantasy Teams ({len(teams)}):")
            
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Team Name", style="magenta")
            table.add_column("Budget Left", style="green")
            table.add_column("Total Points", style="yellow")
            table.add_column("Free Transfers", style="blue")
            
            for team in teams:
                table.add_row(
                    str(team.id),
                    team.name,
                    f"${team.budget_remaining:,.0f}",
                    f"{team.total_points:.1f}",
                    str(team.free_transfers)
                )
            
            console.print(table)
        else:
            console.print("\nNo fantasy teams created yet.")
            console.print("Use 'fantasy-cli team create' to create your first team!")

@user_commands.command()
@click.option('--user-id', type=int, prompt='User ID', help='User ID to delete')
@click.confirmation_option(prompt='Are you sure you want to delete this user?')
def delete(user_id):
    """Delete a user (WARNING: This will delete all associated teams!)"""
    app = get_app()
    db = get_db()
    
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            console.print("User not found", style="red")
            return
        
        try:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            
            console.print(f"User '{username}' deleted successfully!", style="green")
            
        except Exception as e:
            console.print(f"Error deleting user: {e}", style="red")
            db.session.rollback()
