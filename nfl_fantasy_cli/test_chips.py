from app.database import get_app, get_db
from app.models import NFLPlayer, FantasyTeam, WeeklyLineup, WeeklyScore, TeamPlayer
from app.fantasy_logic import calculate_team_score

def test_chips():
    app = get_app()
    with app.app_context():
        db = get_db()
        print("🧪 Testing Fantasy Chips...")
        
        # Get Dream Team
        team = FantasyTeam.query.filter_by(name="The Dream Team").first()
        if not team:
            print("❌ Dream Team not found. Run create_dream_team.py first.")
            return

        # Get Mahomes
        mahomes = NFLPlayer.query.filter_by(name="Patrick Mahomes").first()
        
        # Mock score for Mahomes
        score = WeeklyScore(
            player_id=mahomes.id,
            week=1,
            season=2024,
            fantasy_points=20.0  # 20 points base
        )
        db.session.add(score)
        db.session.commit()
        
        # Test 1: Triple Captain
        print("\nTesting Triple Captain...")
        lineup = WeeklyLineup.query.filter_by(team_id=team.id, week=1).first()
        lineup.captain_id = mahomes.id
        lineup.chip_used = 'triple_captain'
        db.session.commit()
        
        result = calculate_team_score(team.id, 1, 2024)
        
        mahomes_points = result['position_breakdown']['QB']['points']
        print(f"Mahomes Base Points: 20.0")
        print(f"Mahomes Triple Captain Points: {mahomes_points}")
        
        if mahomes_points == 60.0:
            print("✅ Triple Captain Logic Worked (20 * 3 = 60)")
        else:
            print(f"❌ Triple Captain Failed. Expected 60.0, got {mahomes_points}")

        # Test 2: Bench Boost
        print("\nTesting Bench Boost...")
        # Add a bench player
        burrow = NFLPlayer.query.filter_by(name="Joe Burrow").first()
        
        # Mock score for Burrow
        score_burrow = WeeklyScore(
            player_id=burrow.id,
            week=1,
            season=2024,
            fantasy_points=15.0
        )
        db.session.add(score_burrow)
        
        lineup.chip_used = 'bench_boost'
        db.session.commit()
        
        result = calculate_team_score(team.id, 1, 2024)
        
        bench_points = 0
        for pos, data in result['position_breakdown'].items():
            if 'BENCH' in pos:
                print(f"Found Bench Player: {pos} - {data['points']} pts")
                bench_points += data['points']
                
        if bench_points > 0:
            print(f"✅ Bench Boost Logic Worked. Bench Points: {bench_points}")
        else:
            print("❌ Bench Boost Failed. No bench points found.")

if __name__ == "__main__":
    test_chips()
