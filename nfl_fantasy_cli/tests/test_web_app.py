import pytest
from web_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'NFL Fantasy League' in rv.data

def test_leaderboard(client):
    rv = client.get('/leaderboard')
    assert rv.status_code == 200
    assert b'Leaderboard' in rv.data

def test_teams(client):
    rv = client.get('/teams')
    assert rv.status_code == 200
    assert b'All Teams' in rv.data

def test_players(client):
    rv = client.get('/players')
    assert rv.status_code == 200
    assert b'NFL Players' in rv.data
