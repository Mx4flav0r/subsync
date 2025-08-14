#!/usr/bin/env python3
"""
Debug credential loading issues
"""

from database_manager import DatabaseManager
from credential_manager import CredentialManager

print("🔍 DEBUGGING CREDENTIAL LOADING")
print("=" * 50)

# Test database manager directly
print("\n1. Testing DatabaseManager directly:")
db_manager = DatabaseManager()
url, api_key = db_manager.load_bazarr_credentials()
print(f"   URL: {url}")
print(f"   API Key: {api_key}")
print(f"   Both present: {bool(url and api_key)}")

# Test credential manager
print("\n2. Testing CredentialManager:")
credential_manager = CredentialManager(db_manager)
print(f"   bazarr_url: {credential_manager.bazarr_url}")
print(f"   bazarr_api_key: {credential_manager.bazarr_api_key}")
print(f"   is_configured: {credential_manager.is_bazarr_configured()}")

print("\n✅ Debug complete!")
