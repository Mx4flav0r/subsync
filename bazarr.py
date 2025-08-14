#!/usr/bin/env python3
"""
Bazarr Service Integration Module
Wrapper around the existing BazarrIntegration with enhanced functionality
"""

import os
import requests
import json
from typing import Dict, List, Tuple, Optional, Any
from config import config
from database import database

# Import your existing powerful Bazarr integration
try:
    from bazarr_integration import BazarrIntegration as CoreBazarrIntegration
    from credential_manager import CredentialManager
except ImportError:
    print("⚠️ Could not import bazarr_integration.py - using fallback implementation")
    CoreBazarrIntegration = None
    CredentialManager = None

class BazarrService:
    """Enhanced Bazarr service using your existing BazarrIntegration"""
    
    def __init__(self):
        # Initialize with existing credential manager if available
        if CredentialManager:
            # Use your existing database manager for credentials
            try:
                from database_manager import DatabaseManager as CoreDB
                core_db = CoreDB()
            except ImportError:
                core_db = None
            
            if core_db:
                self.credential_manager = CredentialManager(core_db)
                self.core_integration = CoreBazarrIntegration(self.credential_manager) if CoreBazarrIntegration else None
                self.use_core = True
                print("✅ Using your existing powerful BazarrIntegration")
            else:
                self.credential_manager = None
                self.core_integration = None
                self.use_core = False
        else:
            self.credential_manager = None
            self.core_integration = None
            self.use_core = False
            print("⚠️ Using fallback Bazarr implementation")
        
        # Load configuration
        self.url = None
        self.api_key = None
        self.load_credentials()
        
        # Cache for media data
        self.movies_cache = []
        self.series_cache = []
        self.cache_valid = False
    
    def load_credentials(self):
        """Load Bazarr credentials from database, file, or config"""
        if self.use_core and self.credential_manager:
            # Use existing credential manager
            self.url = self.credential_manager.bazarr_url
            self.api_key = self.credential_manager.bazarr_api_key
        else:
            # Try multiple sources for credentials
            self.url = "http://192.168.90.3:30046"
            self.api_key = "900109438dd185938a382344cd28c88a"
            
            # Try to load from file first
            try:
                import json
                cred_file = "bazarr_credentials.json"
                if os.path.exists(cred_file):
                    with open(cred_file, 'r') as f:
                        creds = json.load(f)
                        self.url = creds.get('url', self.url)
                        self.api_key = creds.get('api_key', self.api_key)
                        print("✅ Loaded credentials from file")
                else:
                    # Save default credentials to file
                    with open(cred_file, 'w') as f:
                        json.dump({'url': self.url, 'api_key': self.api_key}, f)
                        print("✅ Saved default credentials to file")
            except Exception as e:
                print(f"⚠️ Could not load/save credentials file: {e}")
            
            # Try database as backup
            try:
                url, api_key = database.get_credentials("bazarr")
                if url and api_key:
                    self.url = url
                    self.api_key = api_key
                    print("✅ Loaded credentials from database")
            except Exception as e:
                print(f"⚠️ Database credential load failed: {e}")
                
            # Always ensure we have the hardcoded defaults
            if not self.url:
                self.url = "http://192.168.90.3:30046"
            if not self.api_key:
                self.api_key = "900109438dd185938a382344cd28c88a"
    
    def is_configured(self) -> bool:
        """Check if Bazarr is properly configured"""
        if self.use_core and self.credential_manager:
            return self.credential_manager.is_bazarr_configured()
        else:
            return bool(self.url and self.api_key)
    
    def configure_credentials(self) -> bool:
        """Configure Bazarr credentials interactively"""
        if self.use_core and self.credential_manager:
            # Use existing credential configuration
            success = self.credential_manager.configure_bazarr_credentials()
            if success:
                self.url = self.credential_manager.bazarr_url
                self.api_key = self.credential_manager.bazarr_api_key
            return success
        else:
            # Fallback implementation
            return self._configure_credentials_fallback()
    
    def _configure_credentials_fallback(self) -> bool:
        """Fallback credential configuration"""
        print("\n🔧 BAZARR CONFIGURATION")
        print("=" * 50)
        
        current_url = self.url or config.get("bazarr_url")
        url = input(f"Bazarr URL [{current_url}]: ").strip() or current_url
        
        print(f"\n🔑 Find your API key at: {url}/settings/general")
        api_key = input("Bazarr API key: ").strip()
        
        if not api_key:
            print("❌ API key required")
            return False
        
        # Test connection
        if self.test_connection(url, api_key):
            self.url = url
            self.api_key = api_key
            
            # Save to database
            success = database.save_credentials("bazarr", url, api_key)
            if success:
                print("✅ Bazarr credentials configured successfully!")
                return True
            else:
                print("❌ Failed to save credentials")
                return False
        else:
            print("❌ Failed to connect to Bazarr")
            return False
    
    def test_connection(self, url: str = None, api_key: str = None) -> bool:
        """Test Bazarr connection"""
        if self.use_core and self.credential_manager:
            test_url = url or self.url
            test_api_key = api_key or self.api_key
            
            # Use existing integration to test connection
            return self.core_integration.test_connection(test_url, test_api_key)
        else:
            # Fallback to simple request
            try:
                response = requests.get(f"{url or self.url}/api/system/status", headers={"X-API-KEY": api_key or self.api_key})
                return response.status_code == 200
            except Exception as e:
                print(f"❌ Error testing connection: {e}")
                return False
    
    def refresh_media_data(self):
        """Refresh cached media data from Bazarr"""
        if not self.is_configured():
            print("⚠️ Bazarr is not configured")
            return
        
        # Debug configuration
        print(f"🔧 Bazarr URL: {self.url}")
        print(f"🔑 API Key: {'***' + (self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else 'None')}")
        
        if self.use_core and self.core_integration:
            # Use existing integration to refresh data
            self.core_integration.refresh_media_data()
        else:
            # Fallback to manual API calls
            self.refresh_movies()
            self.refresh_series()
    
    def refresh_movies(self):
        """Refresh movie data"""
        if not self.url or not self.api_key:
            print("⚠️ Bazarr URL or API key not set - please configure Bazarr first")
            self.movies_cache = []
            return
        
        try:
            # Request all movies using simple endpoint (no pagination params)
            response = requests.get(f"{self.url}/api/movies", 
                                  headers={"X-API-KEY": self.api_key})
            print(f"📡 Movies API response: {response.status_code}")
            print(f"📡 API URL: {self.url}/api/movies")
            
            if response.status_code == 200:
                if response.text.strip():
                    try:
                        raw_data = response.json()
                        
                        # Handle Bazarr API wrapper format {"data": [...]}
                        if isinstance(raw_data, dict) and 'data' in raw_data:
                            self.movies_cache = raw_data['data']
                            print(f"✅ Extracted {len(self.movies_cache)} movies from data wrapper")
                        elif isinstance(raw_data, list):
                            self.movies_cache = raw_data
                            print(f"✅ Using direct movies list with {len(self.movies_cache)} items")
                        else:
                            print(f"❌ Unexpected API response format: {type(raw_data)}")
                            print(f"📝 Raw data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
                            self.movies_cache = []
                            return
                        
                        self.cache_valid = True
                        print(f"✅ Refreshed {len(self.movies_cache)} movies")
                        
                        # Debug: Show first movie structure
                        if self.movies_cache:
                            print(f"🔍 First movie type: {type(self.movies_cache[0])}")
                            if isinstance(self.movies_cache[0], dict) and self.movies_cache[0]:
                                print(f"🔍 Movie keys: {list(self.movies_cache[0].keys())[:5]}...")
                                # Show the actual title to help with search debugging
                                title = self.movies_cache[0].get('title', 'No title field')
                                print(f"🔍 First movie title: '{title}'")
                            else:
                                print(f"🔍 First movie: {str(self.movies_cache[0])[:100]}...")
                        
                        print(f"✅ Movies cache successfully populated with {len(self.movies_cache)} items")
                    except ValueError as e:
                        print(f"❌ Invalid JSON response from movies API: {e}")
                        print(f"📝 Response content: {response.text[:200]}...")
                        self.movies_cache = []
                    except Exception as json_error:
                        print(f"❌ Unexpected error parsing movies JSON: {json_error}")
                        print(f"📝 Response content: {response.text[:200]}...")
                        self.movies_cache = []
                else:
                    print("❌ Empty response from movies API")
                    self.movies_cache = []
            else:
                print(f"❌ Failed to refresh movies: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}...")
                self.movies_cache = []
        except Exception as e:
            print(f"❌ Error refreshing movies: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"📝 Full traceback:")
            traceback.print_exc()
            self.movies_cache = []
    
    def refresh_series(self):
        """Refresh series data"""
        if not self.url or not self.api_key:
            print("⚠️ Bazarr URL or API key not set - please configure Bazarr first")
            self.series_cache = []
            return
        
        try:
            # Request all series using simple endpoint (no pagination params)
            response = requests.get(f"{self.url}/api/series", 
                                  headers={"X-API-KEY": self.api_key})
            print(f"📡 Series API response: {response.status_code}")
            print(f"📡 API URL: {self.url}/api/series")
            print(f"📡 Response size: {len(response.text)} characters")
            
            if response.status_code == 200:
                if response.text.strip():
                    try:
                        raw_data = response.json()
                        
                        # Handle Bazarr API wrapper format {"data": [...]}
                        if isinstance(raw_data, dict) and 'data' in raw_data:
                            self.series_cache = raw_data['data']
                            print(f"✅ Extracted {len(self.series_cache)} series from data wrapper")
                        elif isinstance(raw_data, list):
                            self.series_cache = raw_data
                            print(f"✅ Using direct series list with {len(self.series_cache)} items")
                        else:
                            print(f"❌ Unexpected API response format: {type(raw_data)}")
                            print(f"📝 Raw data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
                            self.series_cache = []
                            return
                        
                        self.cache_valid = True
                        print(f"✅ Refreshed {len(self.series_cache)} series")
                        
                        # Debug: Show first series structure
                        if self.series_cache:
                            print(f"🔍 First series type: {type(self.series_cache[0])}")
                            if isinstance(self.series_cache[0], dict) and self.series_cache[0]:
                                print(f"🔍 Series keys: {list(self.series_cache[0].keys())[:5]}...")
                                # Show the actual title to help with search debugging
                                title = self.series_cache[0].get('title', 'No title field')
                                print(f"🔍 First series title: '{title}'")
                            else:
                                print(f"🔍 First series: {str(self.series_cache[0])[:100]}...")
                        
                        print(f"✅ Series cache successfully populated with {len(self.series_cache)} items")
                    except ValueError as e:
                        print(f"❌ Invalid JSON response from series API: {e}")
                        print(f"📝 Response content: {response.text[:200]}...")
                        self.series_cache = []
                    except Exception as json_error:
                        print(f"❌ Unexpected error parsing series JSON: {json_error}")
                        print(f"📝 Response content: {response.text[:200]}...")
                        self.series_cache = []
                else:
                    print("❌ Empty response from series API")
                    self.series_cache = []
            else:
                print(f"❌ Failed to refresh series: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}...")
                self.series_cache = []
        except Exception as e:
            print(f"❌ Error refreshing series: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"📝 Full traceback:")
            traceback.print_exc()
            self.series_cache = []
    
    def get_movies(self) -> List[Dict[str, Any]]:
        """Get cached movie data"""
        if not self.cache_valid:
            self.refresh_movies()
        
        return self.movies_cache
    
    def get_series(self) -> List[Dict[str, Any]]:
        """Get cached series data"""
        if not self.cache_valid:
            self.refresh_series()
        
        return self.series_cache
    
    def search_movies(self, query: str) -> List[Dict[str, Any]]:
        """Search for movies by title"""
        all_movies = self.get_movies()
        matches = []
        
        for movie in all_movies:
            try:
                if isinstance(movie, dict):
                    title = movie.get("title", "").lower()
                elif isinstance(movie, str):
                    # If movie is a string, try to find the title in it
                    title = movie.lower()
                else:
                    print(f"⚠️ Unexpected movie data type: {type(movie)}")
                    continue
                    
                if query.lower() in title:
                    # Ensure we return a dict format
                    if isinstance(movie, dict):
                        matches.append(movie)
                    else:
                        # Convert string to dict format
                        matches.append({"title": movie, "type": "movie"})
            except Exception as e:
                print(f"⚠️ Error processing movie in search: {e}")
                continue
                
        return matches
    
    def search_series(self, query: str) -> List[Dict[str, Any]]:
        """Search for series by title"""
        all_series = self.get_series()
        matches = []
        
        for serie in all_series:
            try:
                if isinstance(serie, dict):
                    title = serie.get("title", "").lower()
                elif isinstance(serie, str):
                    # If serie is a string, try to find the title in it
                    title = serie.lower()
                else:
                    print(f"⚠️ Unexpected series data type: {type(serie)}")
                    continue
                    
                if query.lower() in title:
                    # Ensure we return a dict format
                    if isinstance(serie, dict):
                        matches.append(serie)
                    else:
                        # Convert string to dict format
                        matches.append({"title": serie, "type": "series"})
            except Exception as e:
                print(f"⚠️ Error processing series in search: {e}")
                continue
                
        return matches
    
    def debug_data_structure(self):
        """Debug method to show what data structure Bazarr returns"""
        print("\n🔍 BAZARR DATA STRUCTURE DEBUG")
        print("=" * 50)
        
        movies = self.get_movies()
        series = self.get_series()
        
        print(f"Movies: {len(movies)} items")
        if movies:
            print(f"  First movie type: {type(movies[0])}")
            print(f"  First movie: {str(movies[0])[:100]}...")
            if isinstance(movies[0], dict):
                print(f"  Movie keys: {list(movies[0].keys())}")
        
        print(f"\nSeries: {len(series)} items")
        if series:
            print(f"  First series type: {type(series[0])}")
            print(f"  First series: {str(series[0])[:100]}...")
            if isinstance(series[0], dict):
                print(f"  Series keys: {list(series[0].keys())}")
        
        print("=" * 50)
    
    def get_all_media(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Get all media (movies and series) from Bazarr"""
        movies = self.get_movies()
        series = self.get_series()
        return movies, series


# Simple global instance for backward compatibility
bazarr = None

def init_bazarr():
    """Initialize the global bazarr instance"""
    global bazarr
    if bazarr is None:
        bazarr = BazarrService()
    return bazarr

# Initialize immediately
bazarr = BazarrService()
