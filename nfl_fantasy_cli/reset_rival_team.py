from app.database import get_app, get_db
from app.models import FantasyTeam

app = get_app()
with app.app_context():
    db = get_db()
    FantasyTeam.query.filter_by(name='The Underdogs').delete()
    db.session.commit()
    print('Deleted The Underdogs')
