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

# Use SQLite for local development (PostgreSQL dependencies removed)
import os
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'nfl_fantasy.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
print("✅ Using local SQLite database for development")

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
            print(f"📊 Tables in database: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            print("💡 Make sure your SUPABASE_DB_URL is correct and you have proper permissions")

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
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

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
