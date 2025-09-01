from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Supabase Configuration
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Configure SQLAlchemy to connect to Supabase PostgreSQL
if SUPABASE_DB_URL:
    # Convert psycopg3 URL to psycopg2 format for SQLAlchemy compatibility
    if SUPABASE_DB_URL.startswith('postgresql://'):
        # SQLAlchemy with psycopg3 uses postgresql+psycopg://
        modified_url = SUPABASE_DB_URL.replace('postgresql://', 'postgresql+psycopg://')
        app.config['SQLALCHEMY_DATABASE_URI'] = modified_url
        print(f"✅ Connected to Supabase database: {SUPABASE_DB_URL.split('@')[1] if '@' in SUPABASE_DB_URL else 'Database URL configured'}")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_DB_URL
else:
    # Fallback to local SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nfl_fantasy.db'
    print("⚠️  Using local SQLite database (SUPABASE_DB_URL not found)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0
}

db = SQLAlchemy(app)

def init_db():
    """Initialize the database with all tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify connection by checking if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables in database: {', '.join(tables)}")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            print("Make sure your SUPABASE_DB_URL is correct and you have proper permissions")

def get_app():
    """Get the Flask app instance"""
    return app

def get_db():
    """Get the database instance"""
    return db

def test_connection():
    """Test the database connection"""
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
