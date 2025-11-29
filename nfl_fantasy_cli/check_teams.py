from app.database import get_app
from app.models import FantasyTeam

app = get_app()
with app.app_context():
    teams = FantasyTeam.query.all()
    print(f"Found {len(teams)} teams:")
    for t in teams:
        print(f"- {t.name} (ID: {t.id})")
