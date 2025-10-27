#!/usr/bin/env python3
import click
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, get_app
from app.commands.user import user_commands
from app.commands.team import team_commands  
from app.commands.gameweek import gameweek_commands
from app.commands.data import data_commands
from app.commands.api import api_commands

@click.group()
def cli():
    """NFL Fantasy League CLI - Manage your fantasy team from the command line!"""
    pass

@cli.command()
def init():
    """Initialize the database with all tables"""
    try:
        init_db()
        click.echo("Database initialized successfully!")
    except Exception as e:
        click.echo(f"Error initializing database: {e}")

@cli.command()
def status():
    """Show system status"""
    click.echo("NFL Fantasy League CLI")
    click.echo("Status: Running")
    click.echo("Database: SQLite")
    
    # Check database connection
    try:
        app = get_app()
        with app.app_context():
            from app.models import User
            # Ensure tables exist
            from app.database import db
            db.create_all()
            
            user_count = User.query.count()
            click.echo(f"Users registered: {user_count}")
            click.echo("Database connection: ✅ Connected")
    except Exception as e:
        click.echo(f"Database connection: Error - {e}")

# Register command groups
cli.add_command(user_commands)
cli.add_command(team_commands)
cli.add_command(gameweek_commands)
cli.add_command(data_commands)
cli.add_command(api_commands)

if __name__ == '__main__':
    cli()