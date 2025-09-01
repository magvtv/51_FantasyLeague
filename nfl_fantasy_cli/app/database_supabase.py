from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

# Alternative: Parse from Supabase URL if you prefer
if not SUPABASE_DB_URL and SUPABASE_URL:
    # Extract database URL from Supabase project URL
    # You'll get this from your Supabase project settings > Database > Connection string
    SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', f'postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT_REF].supabase.co:5432/postgres')

app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def init_db():
    """Initialize the database with all tables"""
    with app.app_context():
        db.create_all()
        print("✅ Supabase database tables created successfully!")

def get_app():
    """Get the Flask app instance"""
    return app

def get_db():
    """Get the database instance"""
    return db

# Optional: Add Supabase client for additional features like Auth, Realtime, etc.
def get_supabase_client():
    """Get Supabase client for additional features (optional)"""
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except ImportError:
        print("⚠️  supabase-py not installed. Run: pip install supabase")
        return None
