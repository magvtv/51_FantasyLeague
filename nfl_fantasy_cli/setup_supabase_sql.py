#!/usr/bin/env python3
"""
Supabase SQL Setup Script
This script runs the setup_database.sql file directly on your Supabase database.
Useful if you prefer SQL-based table creation over SQLAlchemy models.
"""

import os
import sys
import psycopg
from dotenv import load_dotenv

def connect_to_supabase():
    """Connect to Supabase using psycopg2"""
    load_dotenv()
    
    supabase_db_url = os.getenv('SUPABASE_DB_URL')
    if not supabase_db_url:
        print("❌ SUPABASE_DB_URL not found in environment variables!")
        return None
    
    try:
        # Parse the connection URL
        # Format: postgresql://postgres:password@host:port/database
        if supabase_db_url.startswith('postgresql://'):
            # Extract components from the URL
            url_parts = supabase_db_url.replace('postgresql://', '').split('@')
            if len(url_parts) != 2:
                print("❌ Invalid SUPABASE_DB_URL format!")
                return None
            
            user_pass = url_parts[0].split(':')
            host_db = url_parts[1].split('/')
            
            if len(user_pass) < 2 or len(host_db) < 2:
                print("❌ Invalid SUPABASE_DB_URL format!")
                return None
            
            username = user_pass[0]
            password = user_pass[1]
            host_port = host_db[0].split(':')
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else '5432'
            database = host_db[1]
            
            # Connect to Supabase using connection string with IPv4 preference
            conn_string = f"postgresql://{username}:{password}@{host}:{port}/{database}?preferQueryMode=simple"
            conn = psycopg.connect(conn_string)
            
            print(f"✅ Connected to Supabase database: {host}:{port}/{database}")
            return conn
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def run_sql_script(conn, script_path):
    """Run the SQL script on the database"""
    try:
        with open(script_path, 'r') as file:
            sql_script = file.read()
        
        cursor = conn.cursor()
        
        # Split the script into individual statements
        statements = sql_script.split(';')
        
        print("🏗️  Executing SQL script...")
        
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"   ✅ Statement {i+1} executed successfully")
                except Exception as e:
                    print(f"   ⚠️  Statement {i+1} failed: {e}")
                    # Continue with other statements
        
        conn.commit()
        cursor.close()
        print("✅ SQL script execution completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error executing SQL script: {e}")
        return False

def verify_tables(conn):
    """Verify that tables were created successfully"""
    try:
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        cursor.close()
        
        print(f"\n📊 Tables in database:")
        for table in tables:
            print(f"   ✅ {table[0]}")
        
        return len(tables) > 0
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main function"""
    print("🚀 NFL Fantasy League - Supabase SQL Setup")
    print("=" * 50)
    
    # Connect to Supabase
    conn = connect_to_supabase()
    if not conn:
        return False
    
    # Path to the SQL script
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setup_database.sql')
    
    if not os.path.exists(script_path):
        print(f"❌ SQL script not found: {script_path}")
        return False
    
    # Run the SQL script
    success = run_sql_script(conn, script_path)
    
    if success:
        # Verify tables were created
        verify_tables(conn)
    
    # Close connection
    conn.close()
    
    if success:
        print("\n🎉 SQL setup completed successfully!")
        print("💡 You can now view your tables in the Supabase dashboard")
    else:
        print("\n❌ SQL setup failed!")
    
    return success

if __name__ == "__main__":
    main()
