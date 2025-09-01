#!/usr/bin/env python3
"""
NFL Fantasy League Database Setup
Simple script to create tables in Supabase using your SQLAlchemy models.
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def main():
    """Main setup function"""
    print("🚀 NFL Fantasy League - Database Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check configuration
    supabase_db_url = os.getenv('SUPABASE_DB_URL')
    if not supabase_db_url:
        print("❌ SUPABASE_DB_URL not found!")
        print("💡 Please check your .env file")
        return False
    
    print(f"✅ Database URL configured")
    
    try:
        # Import database and models
        from database import init_db, test_connection
        
        # Test connection
        print("\n🔍 Testing database connection...")
        if not test_connection():
            print("❌ Connection failed! Check your credentials and IP whitelist.")
            return False
        
        # Create tables
        print("\n🏗️  Creating database tables...")
        init_db()
        
        print("\n🎉 Setup completed successfully!")
        print("💡 You can now view your tables in the Supabase dashboard")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file has correct Supabase credentials")
        print("   2. Ensure your IP is whitelisted in Supabase")
        print("   3. Verify your Supabase project is active")
        print("   4. Try running the SQL script manually in Supabase dashboard")
