#!/usr/bin/env python3
"""
Debug script to test database operations
"""

import os
import sqlite3
from database import database

def test_database_operations():
    print("🔍 DEBUGGING DATABASE OPERATIONS")
    print("=" * 50)
    
    # Check file permissions and existence
    db_path = "subsync.db"
    print(f"📁 Database path: {os.path.abspath(db_path)}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📄 Database file exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        stat = os.stat(db_path)
        print(f"📄 File size: {stat.st_size} bytes")
        print(f"📄 File permissions: {oct(stat.st_mode)}")
        print(f"📄 Readable: {os.access(db_path, os.R_OK)}")
        print(f"📄 Writable: {os.access(db_path, os.W_OK)}")
    
    # Test direct SQLite connection
    print("\n🔧 Testing direct SQLite connection...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)")
        cursor.execute("INSERT INTO test_table DEFAULT VALUES")
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        print(f"✅ Direct SQLite works: {count} test records")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Direct SQLite failed: {e}")
    
    # Test database wrapper
    print("\n🔧 Testing database wrapper...")
    try:
        print(f"Database instance type: {type(database)}")
        print(f"Using core DB: {database.use_core}")
        
        # Test credential operations
        print("\n🔑 Testing credential save...")
        success = database.save_credentials("test", "http://test.com", "test_token")
        print(f"Save result: {success}")
        
        print("\n🔑 Testing credential load...")
        url, token = database.get_credentials("test")
        print(f"Load result: url={url}, token={token}")
        
        # Test Bazarr credentials specifically
        print("\n🔑 Testing Bazarr credentials...")
        success = database.save_credentials("bazarr", "http://192.168.90.3:30046", "900109438dd185938a382344cd28c88a")
        print(f"Bazarr save result: {success}")
        
        url, token = database.get_credentials("bazarr")
        print(f"Bazarr load result: url={url}, token={token}")
        
    except Exception as e:
        print(f"❌ Database wrapper failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_operations()
