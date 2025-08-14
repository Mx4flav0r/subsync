#!/usr/bin/env python3
"""
Comprehensive credential system debugging
"""

def test_credential_system():
    print("🔍 COMPREHENSIVE CREDENTIAL SYSTEM DEBUG")
    print("=" * 60)
    
    # Test 1: Database Manager
    print("\n1️⃣ TESTING DATABASE MANAGER")
    print("-" * 30)
    
    try:
        from database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        print(f"✅ DatabaseManager imported")
        print(f"📊 Main connection: {db_manager.conn is not None}")
        print(f"📊 Sync connection: {db_manager.sync_conn is not None}")
        
        if db_manager.conn:
            # Test credential save/load
            print("\n🔑 Testing database credential operations...")
            
            # Save test credentials
            result = db_manager.save_bazarr_credentials("http://192.168.90.3:30046", "900109438dd185938a382344cd28c88a")
            print(f"Save result: {result}")
            
            # Load credentials
            url, api_key = db_manager.load_bazarr_credentials()
            print(f"Load result: url={url}, api_key={api_key}")
        else:
            print("❌ Database connections failed")
            
    except Exception as e:
        print(f"❌ DatabaseManager failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Credential Manager
    print("\n2️⃣ TESTING CREDENTIAL MANAGER")
    print("-" * 30)
    
    try:
        from credential_manager import CredentialManager
        
        # Try with a working database manager
        if 'db_manager' in locals() and db_manager.conn:
            cred_manager = CredentialManager(db_manager)
            print(f"✅ CredentialManager with valid DB")
            print(f"🌐 Bazarr URL: {cred_manager.bazarr_url}")
            print(f"🔑 Has API key: {cred_manager.bazarr_api_key is not None}")
            print(f"✅ Is configured: {cred_manager.is_bazarr_configured()}")
            
            # Test connection
            if cred_manager.bazarr_url and cred_manager.bazarr_api_key:
                print(f"\n🧪 Testing connection...")
                result = cred_manager.test_bazarr_connection(cred_manager.bazarr_url, cred_manager.bazarr_api_key)
                print(f"Connection test: {result}")
        else:
            print("❌ Cannot test CredentialManager - DB failed")
            
    except Exception as e:
        print(f"❌ CredentialManager failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Database Wrapper
    print("\n3️⃣ TESTING DATABASE WRAPPER")
    print("-" * 30)
    
    try:
        from database import database
        
        print(f"✅ Database wrapper imported")
        print(f"📊 Using core: {database.use_core}")
        print(f"📊 Core DB available: {database.core_db is not None}")
        
        # Test credential operations
        print(f"\n🔑 Testing wrapper credential operations...")
        result = database.save_credentials("test_service", "http://test.com", "test_token")
        print(f"Save test: {result}")
        
        url, token = database.get_credentials("test_service")
        print(f"Load test: url={url}, token={token}")
        
    except Exception as e:
        print(f"❌ Database wrapper failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Bazarr Service
    print("\n4️⃣ TESTING BAZARR SERVICE")
    print("-" * 30)
    
    try:
        from bazarr import bazarr
        
        print(f"✅ Bazarr service imported")
        print(f"🌐 URL: {bazarr.url}")
        print(f"🔑 Has API key: {bazarr.api_key is not None}")
        print(f"✅ Is configured: {bazarr.is_configured()}")
        
        if bazarr.is_configured():
            print(f"\n🧪 Testing API connection...")
            result = bazarr.test_connection()
            print(f"API test: {result}")
        
    except Exception as e:
        print(f"❌ Bazarr service failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 CREDENTIAL SYSTEM DEBUG COMPLETE")

if __name__ == "__main__":
    test_credential_system()
