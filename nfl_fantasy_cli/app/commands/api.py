import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..api_service import nfl_api
from ..database import get_app

console = Console()

@click.group(name='api')
def api_commands():
    """NFL API data exploration and management commands"""
    pass

@api_commands.command()
def endpoints():
    """Show all available NFL API endpoints"""
    console.print(Panel.fit(
        "NFL API Endpoints Status",
        style="bold blue"
    ))
    
    # Available endpoints (actually working)
    available_endpoints = [
        ("Available Endpoints", [
            "nfl-team-listing/v1/data - All NFL teams (WORKING)",
            "nfl-livescores - Live NFL game scores (NEW)",
            "nfl-player-info/v1/data - Detailed player information (NEW)",
            "nfl-team-injuries - Team injury reports (NEW)",
            "nfl-ath-statistics - Player statistics by year (NEW)",
            "nfl-ath-overview - Player overview (NEW)",
            "nfl-ath-standings - Player standings (NEW)",
            "nfl-ondays - NFL calendar (NEW)",
            "nfl-team-roster - Team rosters (NEW)",
            "nfl-team-statistics - Team statistics (NEW)",
            "nfl-single-coaches - Coach details (NEW)"
        ])
    ]
    
    # Placeholder endpoints (not available yet)
    placeholder_endpoints = [
        ("Not Available (Placeholder)", [
            "season_schedule - Complete season schedule",
            "weekly_schedule - Schedule for specific week",
            "daily_schedule - Schedule for specific date",
            "calendar - NFL calendar/schedule",
            "teams/{id} - Specific team details",
            "team_stats - Detailed team statistics",
            "standings - Team standings/rankings",
            "depth_chart/{id} - Team depth chart",
            "players/{id} - Specific player data",
            "players?team={id} - Players by team",
            "player_stats - Detailed player statistics",
            "player_injuries - Player injury information",
            "injuries - Current injury reports",
            "live_scores - Live game scores",
            "games?season={s}&week={w} - Games by week",
            "games/{id} - Detailed game information",
            "play_by_play/{id} - Play-by-play data",
            "game_odds - Betting odds for games",
            "statistics - Player statistics",
            "passing_stats - Passing statistics",
            "rushing_stats - Rushing statistics",
            "receiving_stats - Receiving statistics",
            "defensive_stats - Defensive statistics",
            "kicking_stats - Kicking statistics",
            "news - NFL news articles",
            "team_news - News for specific team",
            "player_news - News for specific player",
            "predictions - Game predictions",
            "player_projections - Player fantasy projections",
            "fantasy_points - Calculated fantasy points",
            "fantasy_rankings - Fantasy rankings by position",
            "fixtures - NFL fixtures/schedule",
            "matches/{id} - Detailed match information",
            "odds - Betting odds for games",
            "league_standings - League standings"
        ])
    ]
    
    # Display available endpoints
    for category, methods in available_endpoints:
        table = Table(title=f"{category}", show_header=True, header_style="bold green")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Description", style="white")
        
        for method in methods:
            if " - " in method:
                endpoint, description = method.split(" - ", 1)
                table.add_row(endpoint, description)
            else:
                table.add_row(method, "")
        
        console.print(table)
        console.print()
    
    # Display placeholder endpoints
    for category, methods in placeholder_endpoints:
        table = Table(title=f"{category}", show_header=True, header_style="bold red")
        table.add_column("Endpoint", style="cyan")
        table.add_column("Description", style="white")
        
        for method in methods:
            if " - " in method:
                endpoint, description = method.split(" - ", 1)
                table.add_row(endpoint, description)
            else:
                table.add_row(method, "")
        
        console.print(table)
        console.print()
    
    # Add information about the API
    console.print(Panel.fit(
        "API Information\n"
        "- Only the teams endpoint is currently working\n"
        "- Other endpoints return placeholder data\n"
        "- Check RapidAPI documentation for endpoint availability\n"
        "- Use 'api test-connection' to verify API status",
        style="bold yellow"
    ))

@api_commands.command()
@click.option('--season', type=int, default=2024, help='Season year')
def season_info(season):
    """Get current season information"""
    console.print(f"Fetching season {season} information...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching season data...", total=None)
        data = nfl_api.get_current_season()
        progress.update(task, description="Season data fetched")
    
    if data:
        console.print(Panel.fit(
            f"Season {season} Information",
            style="bold green"
        ))
        console.print(f"Current Season: {data.get('season', 'N/A')}")
        console.print(f"Season Type: {data.get('type', 'N/A')}")
        console.print(f"Status: {data.get('status', 'N/A')}")
    else:
        console.print("Failed to fetch season information", style="red")

@api_commands.command()
@click.option('--limit', type=int, default=10, help='Number of teams to show')
def teams(limit):
    """Show NFL teams"""
    console.print(f"Fetching NFL teams (showing top {limit})...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching teams...", total=None)
        data = nfl_api.get_team_data()
        progress.update(task, description="Teams fetched")
    
    if data and 'teams' in data:
        teams_list = data['teams'][:limit]
        
        table = Table(title="NFL Teams", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Abbreviation", style="green")
        table.add_column("Conference", style="yellow")
        table.add_column("Division", style="blue")
        
        for team in teams_list:
            table.add_row(
                str(team.get('id', 'N/A')),
                team.get('name', 'N/A'),
                team.get('abbreviation', 'N/A'),
                team.get('conference', 'N/A'),
                team.get('division', 'N/A')
            )
        
        console.print(table)
    else:
        console.print("Failed to fetch teams data", style="red")
        console.print("This might be due to:")
        console.print("   - Missing or invalid RAPIDAPI_KEY")
        console.print("   - API quota exceeded")
        console.print("   - Network connectivity issues")
        console.print("   - API endpoint changes")

@api_commands.command()
@click.option('--team-id', required=True, help='Team ID to get players for')
@click.option('--limit', type=int, default=20, help='Number of players to show')
def players(team_id, limit):
    """Show players for a specific team"""
    console.print(f"Fetching players for team {team_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching players...", total=None)
        data = nfl_api.get_players_by_team(team_id)
        progress.update(task, description="Players fetched")
    
    if data and 'players' in data:
        players_list = data['players'][:limit]
        
        table = Table(title=f"Players for Team {team_id}", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Position", style="green")
        table.add_column("Number", style="yellow")
        table.add_column("Status", style="blue")
        
        for player in players_list:
            table.add_row(
                str(player.get('id', 'N/A')),
                player.get('name', 'N/A'),
                player.get('position', 'N/A'),
                str(player.get('number', 'N/A')),
                player.get('status', 'N/A')
            )
        
        console.print(table)
    else:
        console.print("Failed to fetch players data", style="red")

@api_commands.command()
@click.option('--season', type=int, default=2024, help='Season year')
@click.option('--week', type=int, help='Specific week')
def schedule(season, week):
    """Show NFL schedule"""
    if week:
        console.print(f"Fetching schedule for Season {season}, Week {week}...")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Fetching schedule...", total=None)
            data = nfl_api.get_weekly_schedule(season, week)
            progress.update(task, description="Schedule fetched")
    else:
        console.print(f"Fetching season {season} schedule...")
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Fetching schedule...", total=None)
            data = nfl_api.get_season_schedule(season)
            progress.update(task, description="Schedule fetched")
    
    if data:
        if week:
            console.print(Panel.fit(f"Week {week} Schedule", style="bold green"))
        else:
            console.print(Panel.fit(f"Season {season} Schedule", style="bold green"))
        
        # This would need to be adapted based on actual API response format
        console.print("Schedule data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch schedule data", style="red")

@api_commands.command()
def live_scores():
    """Show live NFL scores"""
    console.print("Fetching live scores...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching live scores...", total=None)
        data = nfl_api.get_live_scores()
        progress.update(task, description="Live scores fetched")
    
    if data:
        console.print(Panel.fit("Live NFL Scores", style="bold green"))
        # This would need to be adapted based on actual API response format
        console.print("Live score data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch live scores", style="red")

@api_commands.command()
@click.option('--limit', type=int, default=5, help='Number of news articles')
def news(limit):
    """Show NFL news"""
    console.print(f"Fetching NFL news (showing {limit} articles)...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching news...", total=None)
        data = nfl_api.get_nfl_news(limit)
        progress.update(task, description="News fetched")
    
    if data:
        console.print(Panel.fit("NFL News", style="bold green"))
        # This would need to be adapted based on actual API response format
        console.print("News data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch news data", style="red")

@api_commands.command()
def injuries():
    """Show current injury report"""
    console.print("Fetching injury report...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching injuries...", total=None)
        data = nfl_api.get_injury_report()
        progress.update(task, description="Injuries fetched")
    
    if data:
        console.print(Panel.fit("NFL Injury Report", style="bold red"))
        # This would need to be adapted based on actual API response format
        console.print("Injury data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch injury data", style="red")

@api_commands.command()
@click.option('--position', help='Position filter (QB, RB, WR, TE, K, DEF)')
@click.option('--season', type=int, default=2024, help='Season year')
@click.option('--week', type=int, help='Specific week')
def rankings(position, season, week):
    """Show fantasy rankings"""
    console.print(f"Fetching fantasy rankings...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching rankings...", total=None)
        data = nfl_api.get_fantasy_rankings(position, season, week)
        progress.update(task, description="Rankings fetched")
    
    if data:
        title = f"Fantasy Rankings"
        if position:
            title += f" - {position}"
        if week:
            title += f" (Week {week})"
        
        console.print(Panel.fit(title, style="bold green"))
        # This would need to be adapted based on actual API response format
        console.print("Rankings data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch rankings data", style="red")

@api_commands.command()
@click.option('--season', type=int, default=2024, help='Season year')
def fixtures(season):
    """Show NFL fixtures"""
    console.print(f"Fetching NFL fixtures for season {season}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching fixtures...", total=None)
        data = nfl_api.get_fixtures(season)
        progress.update(task, description="Fixtures fetched")
    
    if data:
        console.print(Panel.fit(f"NFL Fixtures - Season {season}", style="bold green"))
        # This would need to be adapted based on actual API response format
        console.print("Fixtures data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch fixtures data", style="red")

@api_commands.command()
@click.option('--season', type=int, default=2024, help='Season year')
def standings(season):
    """Show league standings"""
    console.print(f"Fetching league standings for season {season}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching standings...", total=None)
        data = nfl_api.get_league_standings(season)
        progress.update(task, description="Standings fetched")
    
    if data:
        console.print(Panel.fit(f"NFL Standings - Season {season}", style="bold green"))
        # This would need to be adapted based on actual API response format
        console.print("Standings data retrieved from NFL API")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch standings data", style="red")

@api_commands.command()
def cache_info():
    """Show API cache information"""
    info = nfl_api.get_cache_info()
    
    console.print(Panel.fit("API Cache Information", style="bold blue"))
    console.print(f"Cache Size: {info['size']}")
    console.print(f"Max Size: {info['maxsize']}")
    console.print(f"TTL: {info['ttl']} seconds")

@api_commands.command()
def clear_cache():
    """Clear API cache"""
    nfl_api.clear_cache()
    console.print("API cache cleared", style="green")

@api_commands.command()
def test_connection():
    """Test API connection and key validity"""
    console.print("Testing NFL API connection...")
    
    # Test with a simple endpoint
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Testing connection...", total=None)
        data = nfl_api.get_current_season()
        progress.update(task, description="Connection test completed")
    
    if data:
        console.print("API connection successful!", style="green")
        console.print(f"Response: {data}")
    else:
        console.print("API connection failed", style="red")
        console.print("Possible issues:")
        console.print("   - Invalid RAPIDAPI_KEY")
        console.print("   - API quota exceeded")
        console.print("   - Network connectivity issues")
        console.print("   - API endpoint not available")

# =============================================================================
# NEW ENHANCED API COMMANDS
# =============================================================================

@api_commands.command()
@click.option('--player-id', required=True, help='Player ID to get details for')
def player_detail(player_id):
    """Get detailed player information"""
    console.print(f"Fetching detailed information for player {player_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching player details...", total=None)
        data = nfl_api.get_player_detail(player_id)
        progress.update(task, description="Player details fetched")
    
    if data:
        console.print(Panel.fit(f"Player Details - ID {player_id}", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch player details", style="red")

@api_commands.command()
@click.option('--team-id', required=True, help='Team ID to get injuries for')
def team_injuries(team_id):
    """Get team injury report"""
    console.print(f"Fetching injury report for team {team_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching team injuries...", total=None)
        data = nfl_api.get_team_injuries(team_id)
        progress.update(task, description="Team injuries fetched")
    
    if data:
        console.print(Panel.fit(f"Team Injuries - Team {team_id}", style="bold red"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch team injuries", style="red")

@api_commands.command()
@click.option('--player-id', required=True, help='Player ID to get statistics for')
@click.option('--year', type=int, default=2023, help='Year for statistics')
def player_stats(player_id, year):
    """Get player statistics for a specific year"""
    console.print(f"Fetching statistics for player {player_id} ({year})...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching player statistics...", total=None)
        data = nfl_api.get_player_statistics(player_id, year)
        progress.update(task, description="Player statistics fetched")
    
    if data:
        console.print(Panel.fit(f"Player Statistics - ID {player_id} ({year})", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch player statistics", style="red")

@api_commands.command()
@click.option('--player-id', required=True, help='Player ID to get overview for')
def player_overview(player_id):
    """Get player overview"""
    console.print(f"Fetching overview for player {player_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching player overview...", total=None)
        data = nfl_api.get_player_overview(player_id)
        progress.update(task, description="Player overview fetched")
    
    if data:
        console.print(Panel.fit(f"Player Overview - ID {player_id}", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch player overview", style="red")

@api_commands.command()
@click.option('--player-id', required=True, help='Player ID to get standings for')
def player_standings(player_id):
    """Get player standings"""
    console.print(f"Fetching standings for player {player_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching player standings...", total=None)
        data = nfl_api.get_player_standings(player_id)
        progress.update(task, description="Player standings fetched")
    
    if data:
        console.print(Panel.fit(f"Player Standings - ID {player_id}", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch player standings", style="red")

@api_commands.command()
def calendar():
    """Get NFL calendar"""
    console.print("Fetching NFL calendar...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching calendar...", total=None)
        data = nfl_api.get_nfl_calendar_ondays()
        progress.update(task, description="Calendar fetched")
    
    if data:
        console.print(Panel.fit("NFL Calendar", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch calendar", style="red")

@api_commands.command()
@click.option('--team-id', required=True, help='Team ID to get roster for')
def team_roster(team_id):
    """Get team roster"""
    console.print(f"Fetching roster for team {team_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching team roster...", total=None)
        data = nfl_api.get_team_players(team_id)
        progress.update(task, description="Team roster fetched")
    
    if data:
        console.print(Panel.fit(f"Team Roster - Team {team_id}", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch team roster", style="red")

@api_commands.command()
@click.option('--team-id', required=True, help='Team ID to get statistics for')
@click.option('--year', type=int, default=2023, help='Year for statistics')
def team_statistics(team_id, year):
    """Get team statistics"""
    console.print(f"Fetching statistics for team {team_id} ({year})...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching team statistics...", total=None)
        data = nfl_api.get_team_statistics(team_id, year)
        progress.update(task, description="Team statistics fetched")
    
    if data:
        console.print(Panel.fit(f"Team Statistics - Team {team_id} ({year})", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch team statistics", style="red")

@api_commands.command()
@click.option('--coach-id', required=True, help='Coach ID to get details for')
def coach_details(coach_id):
    """Get coach details"""
    console.print(f"Fetching details for coach {coach_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Fetching coach details...", total=None)
        data = nfl_api.get_coach_details(coach_id)
        progress.update(task, description="Coach details fetched")
    
    if data:
        console.print(Panel.fit(f"Coach Details - ID {coach_id}", style="bold green"))
        console.print(f"Data retrieved: {len(str(data))} characters")
        console.print("(Display format would depend on actual API response structure)")
    else:
        console.print("Failed to fetch coach details", style="red")

# =============================================================================
# DATA SYNC COMMANDS
# =============================================================================

@api_commands.command()
def sync_live_scores():
    """Sync live scores to database"""
    console.print("Syncing live scores to database...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Syncing live scores...", total=None)
        result = nfl_api.sync_live_scores_to_db()
        progress.update(task, description="Live scores synced")
    
    if result.get('success'):
        console.print("Live scores synced successfully!", style="green")
        console.print(f"Message: {result.get('message')}")
    else:
        console.print(f"Failed to sync live scores: {result.get('message')}", style="red")

@api_commands.command()
@click.option('--player-id', required=True, help='Player ID to sync details for')
def sync_player_details(player_id):
    """Sync player details to database"""
    console.print(f"Syncing player details for {player_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Syncing player details...", total=None)
        result = nfl_api.sync_player_details_to_db(player_id)
        progress.update(task, description="Player details synced")
    
    if result.get('success'):
        console.print("Player details synced successfully!", style="green")
        console.print(f"Message: {result.get('message')}")
    else:
        console.print(f"Failed to sync player details: {result.get('message')}", style="red")

@api_commands.command()
@click.option('--team-id', required=True, help='Team ID to sync injuries for')
def sync_team_injuries(team_id):
    """Sync team injuries to database"""
    console.print(f"Syncing injuries for team {team_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Syncing team injuries...", total=None)
        result = nfl_api.sync_team_injuries_to_db(team_id)
        progress.update(task, description="Team injuries synced")
    
    if result.get('success'):
        console.print("Team injuries synced successfully!", style="green")
        console.print(f"Message: {result.get('message')}")
    else:
        console.print(f"Failed to sync team injuries: {result.get('message')}", style="red")

@api_commands.command()
def sync_all_rosters():
    """Sync all team rosters to database"""
    console.print("Syncing all team rosters to database...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Syncing all rosters...", total=None)
        result = nfl_api.sync_all_team_rosters()
        progress.update(task, description="All rosters synced")
    
    if result.get('success'):
        console.print("All rosters synced successfully!", style="green")
        console.print(f"Message: {result.get('message')}")
    else:
        console.print(f"Failed to sync rosters: {result.get('message')}", style="red")

@api_commands.command()
def sync_all_injuries():
    """Sync all team injuries to database"""
    console.print("Syncing all team injuries to database...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Syncing all injuries...", total=None)
        result = nfl_api.sync_all_team_injuries()
        progress.update(task, description="All injuries synced")
    
    if result.get('success'):
        console.print("All injuries synced successfully!", style="green")
        console.print(f"Message: {result.get('message')}")
    else:
        console.print(f"Failed to sync injuries: {result.get('message')}", style="red")

# =============================================================================
# ANALYSIS COMMANDS
# =============================================================================

@api_commands.command()
@click.option('--player-id', required=True, help='Player ID to analyze')
def analyze_player(player_id):
    """Get comprehensive fantasy analysis for a player"""
    console.print(f"Analyzing player {player_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Analyzing player...", total=None)
        result = nfl_api.get_player_fantasy_analysis(player_id)
        progress.update(task, description="Player analysis completed")
    
    if result.get('success'):
        console.print(Panel.fit(f"Player Analysis - ID {player_id}", style="bold green"))
        analysis = result.get('analysis', {})
        console.print(f"Has Data: {analysis.get('has_data', False)}")
        console.print(f"Data Sources: {analysis.get('data_sources', 0)}")
        console.print("Analysis completed successfully!")
    else:
        console.print(f"Failed to analyze player: {result.get('message')}", style="red")

@api_commands.command()
@click.option('--team-id', required=True, help='Team ID to analyze')
def analyze_team(team_id):
    """Get comprehensive fantasy analysis for a team"""
    console.print(f"Analyzing team {team_id}...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Analyzing team...", total=None)
        result = nfl_api.get_team_fantasy_analysis(team_id)
        progress.update(task, description="Team analysis completed")
    
    if result.get('success'):
        console.print(Panel.fit(f"Team Analysis - Team {team_id}", style="bold green"))
        analysis = result.get('analysis', {})
        console.print(f"Has Roster: {analysis.get('has_roster', False)}")
        console.print(f"Has Injuries: {analysis.get('has_injuries', False)}")
        console.print(f"Has Stats: {analysis.get('has_stats', False)}")
        console.print(f"Injury Count: {analysis.get('injury_count', 0)}")
        console.print("Analysis completed successfully!")
    else:
        console.print(f"Failed to analyze team: {result.get('message')}", style="red")

@api_commands.command()
def game_status():
    """Get current game status and live scores"""
    console.print("Getting current game status...")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Getting game status...", total=None)
        result = nfl_api.get_current_game_status()
        progress.update(task, description="Game status retrieved")
    
    if result.get('success'):
        console.print(Panel.fit("Current Game Status", style="bold green"))
        console.print(f"Timestamp: {result.get('timestamp')}")
        console.print("Game status retrieved successfully!")
    else:
        console.print(f"Failed to get game status: {result.get('message')}", style="red")
