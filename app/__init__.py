from flask import Flask
from flask_pymongo import pymongo
from flask_jwt_extended import JWTManager
from .nfl_api_service import NFLApiService

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/fantasy_league'
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

mongo = pymongo(app)
jwt = JWTManager(app)
nfl_api = NFLApiService()

from app import routes, models, fantasy_logic