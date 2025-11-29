from app.database import get_app, get_db
from app.models import User, FantasyTeam, NFLPlayer, TeamPlayer, WeeklyLineup
from datetime import datetime

def create_dream_team():
    app = get_app()
    with app.app_context():
        db = get_db()
        
        print("🏈 Creating Dream Team...")
        
        # 1. Create User
        user = User.query.filter_by(username="DreamUser").first()
        if not user:
            user = User(username="DreamUser", email="dream@example.com")
            db.session.add(user)
            db.session.commit()
            print("✅ Created User: DreamUser")
        else:
            print("ℹ️  User DreamUser already exists")
            
        # 2. Create Team
        team = FantasyTeam.query.filter_by(name="The Dream Team").first()
        if not team:
            team = FantasyTeam(
                name="The Dream Team",
                user_id=user.id,
                budget_remaining=100000000,
                total_points=0
            )
            db.session.add(team)
            db.session.commit()
            print("✅ Created Team: The Dream Team")
        else:
            print("ℹ️  Team 'The Dream Team' already exists")
            
        # 3. Define Star Players
        star_players = [
            # QB
            {"nfl_id": "3139477", "name": "Patrick Mahomes", "position": "QB", "team": "KC", "price": 12000000},
            # RB
            {"nfl_id": "3903875", "name": "Christian McCaffrey", "position": "RB", "team": "SF", "price": 11000000},
            {"nfl_id": "3043078", "name": "Derrick Henry", "position": "RB", "team": "BAL", "price": 9000000},
            # WR
            {"nfl_id": "3116406", "name": "Tyreek Hill", "position": "WR", "team": "MIA", "price": 10500000},
            {"nfl_id": "4262921", "name": "Justin Jefferson", "position": "WR", "team": "MIN", "price": 10000000},
            # TE
            {"nfl_id": "15847", "name": "Travis Kelce", "position": "TE", "team": "KC", "price": 8500000},
            # K
            {"nfl_id": "15683", "name": "Justin Tucker", "position": "K", "team": "BAL", "price": 4000000},
            # DEF
            {"nfl_id": "SF_DEF", "name": "49ers Defense", "position": "DEF", "team": "SF", "price": 5000000},
            # Bench / Extra
            {"nfl_id": "4241464", "name": "Joe Burrow", "position": "QB", "team": "CIN", "price": 10000000},
            {"nfl_id": "4242335", "name": "Ja'Marr Chase", "position": "WR", "team": "CIN", "price": 9500000},
        ]
        
        # 4. Insert Players and Add to Team
        for p_data in star_players:
            # Check if player exists
            player = NFLPlayer.query.filter_by(nfl_id=p_data["nfl_id"]).first()
            if not player:
                player = NFLPlayer(
                    nfl_id=p_data["nfl_id"],
                    name=p_data["name"],
                    position=p_data["position"],
                    team=p_data["team"],
                    price=p_data["price"],
                    is_injured=False
                )
                db.session.add(player)
                db.session.commit()
                print(f"✅ Created Player: {player.name}")
            
            # Add to Team (if budget allows and not already owned)
            if team.budget_remaining >= player.price:
                existing_ownership = TeamPlayer.query.filter_by(team_id=team.id, player_id=player.id).first()
                if not existing_ownership:
                    tp = TeamPlayer(
                        team_id=team.id,
                        player_id=player.id,
                        purchase_price=player.price
                    )
                    team.budget_remaining -= player.price
                    db.session.add(tp)
                    print(f"💰 Purchased {player.name} for ${player.price:,}")
                else:
                    print(f"ℹ️  Already own {player.name}")
            else:
                print(f"❌ Insufficient funds for {player.name}")
        
        db.session.commit()
        
        # 5. Set Lineup (WeeklyLineup)
        # Find players we just added
        qb = NFLPlayer.query.filter_by(name="Patrick Mahomes").first()
        rb1 = NFLPlayer.query.filter_by(name="Christian McCaffrey").first()
        rb2 = NFLPlayer.query.filter_by(name="Derrick Henry").first()
        wr1 = NFLPlayer.query.filter_by(name="Tyreek Hill").first()
        wr2 = NFLPlayer.query.filter_by(name="Justin Jefferson").first()
        te = NFLPlayer.query.filter_by(name="Travis Kelce").first()
        k = NFLPlayer.query.filter_by(name="Justin Tucker").first()
        def_team = NFLPlayer.query.filter_by(name="49ers Defense").first()
        
        lineup = WeeklyLineup.query.filter_by(team_id=team.id, week=1, season=2024).first()
        if not lineup:
            lineup = WeeklyLineup(
                team_id=team.id,
                week=1,
                season=2024,
                qb_id=qb.id if qb else None,
                rb1_id=rb1.id if rb1 else None,
                rb2_id=rb2.id if rb2 else None,
                wr1_id=wr1.id if wr1 else None,
                wr2_id=wr2.id if wr2 else None,
                te_id=te.id if te else None,
                k_id=k.id if k else None,
                def_id=def_team.id if def_team else None
            )
            db.session.add(lineup)
            db.session.commit()
            print("✅ Set Starting Lineup for Week 1")
        else:
            print("ℹ️  Lineup already set")

        print(f"\n🎉 Dream Team Created! Remaining Budget: ${team.budget_remaining:,}")

if __name__ == "__main__":
    create_dream_team()
