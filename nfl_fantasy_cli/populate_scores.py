from app.database import get_app, get_db
from app.models import NFLPlayer, WeeklyScore, FantasyTeam
from app.fantasy_logic import calculate_team_score
import random

def populate_scores():
    app = get_app()
    with app.app_context():
        db = get_db()
        print("📊 Populating Weekly Scores for Week 1...")
        
        # Get all players
        players = NFLPlayer.query.all()
        
        for player in players:
            # Check if score already exists
            existing = WeeklyScore.query.filter_by(
                player_id=player.id, week=1, season=2024
            ).first()
            
            if existing:
                print(f"ℹ️  Score exists for {player.name}")
                continue
            
            # Generate random realistic stats based on position
            score = WeeklyScore(
                player_id=player.id,
                week=1,
                season=2024
            )
            
            points = 0.0
            
            if player.position == 'QB':
                yds = random.randint(200, 350)
                tds = random.randint(1, 4)
                ints = random.randint(0, 2)
                score.passing_yards = yds
                score.passing_tds = tds
                score.passing_interceptions = ints
                points = (yds / 25) + (tds * 4) - (ints * 2)
                
            elif player.position in ['RB', 'WR', 'TE']:
                yds = random.randint(30, 120)
                tds = random.randint(0, 2)
                rec = random.randint(2, 8)
                score.rushing_yards = yds if player.position == 'RB' else 0
                score.receiving_yards = yds if player.position != 'RB' else random.randint(0, 30)
                score.rushing_tds = tds if player.position == 'RB' else 0
                score.receiving_tds = tds if player.position != 'RB' else 0
                score.receptions = rec
                points = ((score.rushing_yards + score.receiving_yards) / 10) + ((score.rushing_tds + score.receiving_tds) * 6) + rec
                
            elif player.position == 'K':
                fg = random.randint(1, 4)
                xp = random.randint(1, 3)
                score.field_goals_made = fg
                score.extra_points_made = xp
                points = (fg * 3) + xp
                
            elif player.position == 'DEF':
                pa = random.choice([0, 7, 14, 21, 28])
                sacks = random.randint(1, 5)
                int_def = random.randint(0, 2)
                score.def_points_allowed = pa
                score.def_interceptions = int_def
                # Simplified points for DEF
                points = (10 if pa == 0 else 7 if pa <= 6 else 4 if pa <= 13 else 1 if pa <= 20 else 0) + (int_def * 2) + sacks
            
            score.fantasy_points = round(points, 2)
            db.session.add(score)
            print(f"✅ Added score for {player.name}: {points:.2f} pts")
            
        db.session.commit()
        
        # Calculate Team Scores
        teams = FantasyTeam.query.all()
        for team in teams:
            print(f"\n🏆 Calculating score for {team.name}...")
            result = calculate_team_score(team.id, 1, 2024)
            if result['success']:
                print(f"   Total Points: {result['total_points']:.2f}")
            else:
                print(f"   ❌ Failed: {result.get('message')}")

if __name__ == "__main__":
    populate_scores()
