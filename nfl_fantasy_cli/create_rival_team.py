from app.database import get_app, get_db
from app.models import User, FantasyTeam, NFLPlayer, TeamPlayer, WeeklyLineup

def create_rival_team():
    app = get_app()
    with app.app_context():
        db = get_db()
        
        print("🏈 Creating Rival Team...")
        
        # 1. Create User
        user = User.query.filter_by(username="RivalUser").first()
        if not user:
            user = User(username="RivalUser", email="rival@example.com")
            db.session.add(user)
            db.session.commit()
            print("✅ Created User: RivalUser")
            
        # 2. Create Team
        team = FantasyTeam.query.filter_by(name="The Underdogs").first()
        if not team:
            team = FantasyTeam(
                name="The Underdogs",
                user_id=user.id,
                budget_remaining=100000000,
                total_points=0
            )
            db.session.add(team)
            db.session.commit()
            print("✅ Created Team: The Underdogs")
        else:
            print("ℹ️  Team 'The Underdogs' already exists")
            return

        # 3. Define Rival Players (Different from Dream Team)
        rival_players = [
            # QB
            {"nfl_id": "RIVAL_QB_1", "name": "Jalen Hurts", "position": "QB", "team": "PHI", "price": 11500000},
            # RB
            {"nfl_id": "RIVAL_RB_1", "name": "Saquon Barkley", "position": "RB", "team": "PHI", "price": 9500000},
            {"nfl_id": "RIVAL_RB_2", "name": "Alvin Kamara", "position": "RB", "team": "NO", "price": 8500000},
            # WR
            {"nfl_id": "RIVAL_WR_1", "name": "CeeDee Lamb", "position": "WR", "team": "DAL", "price": 10000000},
            {"nfl_id": "RIVAL_WR_2", "name": "Amon-Ra St. Brown", "position": "WR", "team": "DET", "price": 9500000},
            # TE
            {"nfl_id": "RIVAL_TE_1", "name": "George Kittle", "position": "TE", "team": "SF", "price": 7500000},
            # K
            {"nfl_id": "RIVAL_K_1", "name": "Harrison Butker", "position": "K", "team": "KC", "price": 3500000},
            # DEF
            {"nfl_id": "RIVAL_DEF_1", "name": "Ravens Defense", "position": "DEF", "team": "BAL", "price": 4500000},
        ]
        
        # 4. Insert Players and Add to Team
        for p_data in rival_players:
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
            
            # Add to Team
            tp = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                purchase_price=player.price
            )
            team.budget_remaining -= player.price
            db.session.add(tp)
            print(f"💰 Purchased {player.name}")
        
        db.session.commit()
        
        # 5. Set Lineup
        lineup = WeeklyLineup(
            team_id=team.id,
            week=1,
            season=2024,
            qb_id=NFLPlayer.query.filter_by(name="Jalen Hurts").first().id,
            rb1_id=NFLPlayer.query.filter_by(name="Saquon Barkley").first().id,
            rb2_id=NFLPlayer.query.filter_by(name="Alvin Kamara").first().id,
            wr1_id=NFLPlayer.query.filter_by(name="CeeDee Lamb").first().id,
            wr2_id=NFLPlayer.query.filter_by(name="Amon-Ra St. Brown").first().id,
            te_id=NFLPlayer.query.filter_by(name="George Kittle").first().id,
            k_id=NFLPlayer.query.filter_by(name="Harrison Butker").first().id,
            def_id=NFLPlayer.query.filter_by(name="Ravens Defense").first().id
        )
        db.session.add(lineup)
        db.session.commit()
        print("✅ Set Starting Lineup for Week 1")

if __name__ == "__main__":
    create_rival_team()
