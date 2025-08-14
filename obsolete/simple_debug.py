#!/usr/bin/env python3
"""
Simple debug for credential issues - no external dependencies
"""

import sqlite3
import os

print("🔍 DEBUGGING CREDENTIAL ISSUES")
print("=" * 50)

# Check current directory and files
print(f"\n📁 Current directory: {os.getcwd()}")
print(f"📄 Files in directory:")
for file in os.listdir('.'):
    if file.endswith('.db'):
        print(f"   🗄️ {file}")

# Check each database file for bazarr credentials
db_files = [f for f in os.listdir('.') if f.endswith('.db')]

for db_file in db_files:
    print(f"\n🔍 Checking {db_file}:")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"   Tables: {[table[0] for table in tables]}")
        
        # Look for bazarr credentials
        if any('bazarr' in table[0].lower() for table in tables):
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%bazarr%';")
            bazarr_tables = cursor.fetchall()
            for table in bazarr_tables:
                table_name = table[0]
                print(f"   🔍 Checking table {table_name}:")
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                if rows:
                    print(f"      Found {len(rows)} rows")
                    for row in rows:
                        print(f"      Row: {row}")
                else:
                    print("      No data found")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n✅ Debug complete!")
