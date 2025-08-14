#!/usr/bin/env python3
"""
Quick test to verify the fixes work
"""

print("🧪 TESTING FIXES")
print("=" * 50)

print("\n1. Testing PathMapper import:")
try:
    from path_mapper import PathMapper
    print("✅ PathMapper imports successfully")
except Exception as e:
    print(f"❌ PathMapper import failed: {e}")

print("\n2. Testing sync_engine import:")
try:
    from sync_engine import SyncEngine
    print("✅ SyncEngine imports successfully")
except Exception as e:
    print(f"❌ SyncEngine import failed: {e}")

print("\n3. Testing credential_manager:")
try:
    from database_manager import DatabaseManager
    from credential_manager import CredentialManager
    
    db_manager = DatabaseManager()
    credential_manager = CredentialManager(db_manager)
    print(f"✅ CredentialManager created")
    print(f"   📡 Bazarr URL: {credential_manager.bazarr_url}")
    print(f"   🔑 Has API Key: {bool(credential_manager.bazarr_api_key)}")
    print(f"   ✅ Is Configured: {credential_manager.is_bazarr_configured()}")
except Exception as e:
    print(f"❌ CredentialManager test failed: {e}")

print("\n✅ Testing complete!")
