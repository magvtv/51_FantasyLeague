from app import mongo

class User:
    @staticmethod
    def create(username, email, password):
        user = {
            'username': username,
            'email': email,
            'password': password  # Remember to hash this!
        }
        return mongo.db.users.insert_one(user)

class FantasyTeam:
    @staticmethod
    def create(user_id, team_name):
        team = {
            'user_id': user_id,
            'team_name': team_name,
            'players': [],
            'total_points': 0
        }
        return mongo.db.fantasy_teams.insert_one(team)
