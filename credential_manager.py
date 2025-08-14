#!/usr/bin/env python3
"""
Enhanced credential management for Bazarr and Plex integration
"""

import requests
import os

class CredentialManager:
    def __init__(self, db_manager):
        """Initialize credential manager"""
        self.db_manager = db_manager
        self.bazarr_url = None
        self.bazarr_api_key = None
        self.plex_url = None
        self.plex_token = None
        self.plex_client = None
        
        # Try to load existing credentials
        self.load_credentials()
    
    def load_credentials(self):
        """Load all credentials from database"""
        try:
            # Load Bazarr credentials
            bazarr_url, bazarr_api_key = self.db_manager.load_bazarr_credentials()
            print(f"🔍 Loaded from DB - URL: {bazarr_url}, API Key: {'***' + bazarr_api_key[-4:] if bazarr_api_key else None}")
            
            if bazarr_url and bazarr_api_key:
                self.bazarr_url = bazarr_url
                self.bazarr_api_key = bazarr_api_key
                print("🔑 Loaded saved Bazarr credentials")
            else:
                # Use known working credentials as fallback
                self.bazarr_url = "http://192.168.90.3:30046"
                self.bazarr_api_key = "900109438dd185938a382344cd28c88a"
                print("🔧 Using fallback Bazarr credentials")
            
            # Load Plex credentials (if implemented)
            try:
                plex_url, plex_token = self.db_manager.load_plex_credentials()
                if plex_url and plex_token:
                    self.plex_url = plex_url
                    self.plex_token = plex_token
                    print("🔑 Loaded saved Plex credentials")
                    # Initialize Plex client when implemented
                    # self.plex_client = PlexSubtitleManager(plex_url, plex_token)
                else:
                    self.plex_url = "http://192.168.90.3:32400"
                    self.plex_token = None
                    self.plex_client = None
            except AttributeError:
                # Plex methods not implemented yet
                self.plex_url = "http://192.168.90.3:32400"
                self.plex_token = None
                self.plex_client = None
                
        except Exception as e:
            print(f"⚠️ Error loading credentials from database: {e}")
            # Use known working credentials as fallback
            self.bazarr_url = "http://192.168.90.3:30046"
            self.bazarr_api_key = "900109438dd185938a382344cd28c88a"
            print("🔧 Using fallback Bazarr credentials")
            
            # Try to save these credentials for future use
            try:
                self.db_manager.save_bazarr_credentials(self.bazarr_url, self.bazarr_api_key)
                print("💾 Saved fallback credentials to database")
            except Exception as save_error:
                print(f"⚠️ Could not save fallback credentials: {save_error}")
            self.plex_url = "http://192.168.90.3:32400"
            self.plex_token = None
            self.plex_client = None
    
    def is_bazarr_configured(self):
        """Check if Bazarr credentials are configured"""
        return self.bazarr_url is not None and self.bazarr_api_key is not None
    
    def is_plex_configured(self):
        """Check if Plex credentials are configured"""
        return self.plex_url is not None and self.plex_token is not None
    
    def configure_bazarr_credentials(self):
        """Configure Bazarr credentials with user input"""
        print(f"\n🔧 BAZARR CONFIGURATION")
        print("="*50)
        
        # Show current URL
        current_url = self.bazarr_url or "http://192.168.90.3:30046"
        print(f"Current Bazarr URL: {current_url}")
        new_url = input(f"Enter Bazarr server URL [{current_url}]: ").strip()
        
        if not new_url:
            new_url = current_url
        
        print(f"\n🔑 Bazarr API Key Required")
        print(f"💡 You can find your API key in Bazarr Settings > General > Security")
        print(f"💡 Or visit: {new_url}/settings/general")
        
        # Show current API key (masked)
        if self.bazarr_api_key:
            masked_key = self.bazarr_api_key[:8] + "..." + self.bazarr_api_key[-4:]
            print(f"Current API key: {masked_key}")
            new_api_key = input("Enter new Bazarr API key (or press Enter to keep current): ").strip()
            if not new_api_key:
                new_api_key = self.bazarr_api_key
        else:
            new_api_key = input("Enter Bazarr API key: ").strip()
        
        if not new_api_key:
            print("❌ API key is required")
            return False
        
        # Test connection before saving
        print(f"\n🧪 Testing Bazarr connection...")
        print(f"🌐 Server: {new_url}")
        print(f"🔑 API Key: {new_api_key[:8]}...")
        
        if self.test_bazarr_connection(new_url, new_api_key):
            # Save credentials
            if self.db_manager.save_bazarr_credentials(new_url, new_api_key):
                self.bazarr_url = new_url
                self.bazarr_api_key = new_api_key
                print("✅ Bazarr credentials configured successfully!")
                return True
            else:
                print("❌ Failed to save credentials")
                return False
        else:
            print("❌ Failed to configure credentials")
            return False
    
    def configure_plex_credentials(self):
        """Configure Plex credentials - placeholder for now"""
        print(f"\n🎬 PLEX CONFIGURATION")
        print("="*50)
        print("🔧 Plex integration coming soon!")
        print("💡 This will allow auto-configuration of synced subtitles in Plex")
        return False
    
    def test_bazarr_connection(self, url, api_key):
        """Test Bazarr connection"""
        try:
            headers = {'X-API-KEY': api_key}
            response = requests.get(f"{url}/api/system/status", headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Bazarr connection successful!")
                
                # Try to get version info
                try:
                    data = response.json()
                    version = data.get('bazarr_version', 'Unknown')
                    print(f"📱 Version: {version}")
                except:
                    print(f"📱 Version: Unknown")
                
                return True
            elif response.status_code == 401:
                print(f"❌ Authentication failed - check your API key")
                return False
            else:
                print(f"❌ Connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def test_plex_connection(self):
        """Test Plex connection - placeholder"""
        print("🔧 Plex connection testing coming soon!")
        return False
    
    def is_configured(self):
        """Legacy method for backward compatibility"""
        return self.is_bazarr_configured()
    
    def flush_credentials(self):
        """Remove all saved credentials"""
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute("DELETE FROM credentials")
            self.db_manager.conn.commit()
            
            # Clear in-memory credentials
            self.bazarr_url = "http://192.168.90.3:30046"
            self.bazarr_api_key = None
            self.plex_url = "http://192.168.90.3:32400"
            self.plex_token = None
            self.plex_client = None
            
            print("🗑️ All credentials flushed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error flushing credentials: {e}")
            return False