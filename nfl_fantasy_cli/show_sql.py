#!/usr/bin/env python3
"""
Show SQL Setup Script
Displays the SQL content for manual execution in Supabase dashboard.
"""

import os

def show_sql():
    """Display the SQL setup script content"""
    sql_file_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setup_database.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"SQL file not found: {sql_file_path}")
        return
    
    print("Copy this SQL content and paste it into your Supabase SQL Editor:")
    print("=" * 70)
    
    with open(sql_file_path, 'r') as file:
        print(file.read())
    
    print("=" * 70)
    print("Steps to execute:")
    print("   1. Go to your Supabase dashboard")
    print("   2. Click 'SQL Editor' in the left sidebar")
    print("   3. Click 'New Query'")
    print("   4. Paste the content above")
    print("   5. Click 'Run' to execute")

if __name__ == "__main__":
    show_sql()
