from app.database import get_app
from app.models import NFLPlayer

app = get_app()
with app.app_context():
    count = NFLPlayer.query.count()
    print(f"Player count: {count}")
