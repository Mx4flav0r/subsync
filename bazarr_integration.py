#!/usr/bin/env python3
"""
Bazarr API integration using official API documentation
"""

import requests
import json

class BazarrIntegration:
    def __init__(self, credential_manager):
        """Initialize Bazarr integration"""
        self.credential_manager = credential_manager
        self.movies = []
        self.series = []
    
    def test_connection(self, url=None, api_key=None):
        """Test connection to Bazarr server"""
        try:
            test_url = url or self.credential_manager.bazarr_url
            test_api_key = api_key or self.credential_manager.bazarr_api_key
            
            if not test_url or not test_api_key:
                return False
            
            headers = {'X-API-KEY': test_api_key}
            response = requests.get(f"{test_url}/api/system/status", headers=headers, timeout=10)
            
            return response.status_code == 200
                
        except Exception as e:
            print(f"❌ Bazarr connection error: {e}")
            return False
    
    def fetch_media(self):
        """Fetch media from Bazarr using correct API endpoints"""
        try:
            url = self.credential_manager.bazarr_url
            api_key = self.credential_manager.bazarr_api_key
            
            print(f"   Connecting to Bazarr at: {url}")
            print(f"   Using API key: {api_key[:8]}...")
            print("   Testing connectivity...")
            
            # Test connection first
            headers = {'X-API-KEY': api_key}
            
            # Test with system/status endpoint
            response = requests.get(f"{url}/api/system/status", headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("   Bazarr connection successful!")
                status_data = response.json()
                version = status_data.get('bazarr_version', 'unknown')
                print(f"   Bazarr version: {version}")
                
                # Fetch movies using correct endpoint
                print("   Fetching movies from Bazarr...")
                success = self._fetch_movies(url, headers)
                
                if success:
                    # Fetch TV series using correct endpoint  
                    print("   Fetching TV series from Bazarr...")
                    success = self._fetch_series(url, headers)
                
                total_items = len(self.movies) + len(self.series)
                print(f"   Total media items retrieved from Bazarr: {total_items}")
                
                return total_items > 0
                
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed (401) - API key invalid")
                return False
            else:
                print(f"   ❌ Bazarr connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error fetching Bazarr media: {e}")
            return False
    
    def _fetch_movies(self, url, headers):
        """Fetch movies using Bazarr API"""
        try:
            # Use the correct movies endpoint
            response = requests.get(f"{url}/api/movies", headers=headers, timeout=30)
            print(f"   Movies API response: {response.status_code}")
            
            if response.status_code == 200:
                movies_data = response.json()
                
                # Handle both list and dict responses
                if isinstance(movies_data, dict) and 'data' in movies_data:
                    self.movies = movies_data['data']
                elif isinstance(movies_data, list):
                    self.movies = movies_data
                else:
                    print(f"   ⚠️  Unexpected movies data format: {type(movies_data)}")
                    self.movies = []
                
                print(f"   Found {len(self.movies)} movies in Bazarr")
                
                # Debug: Show structure of first movie
                if self.movies:
                    first_movie = self.movies[0]
                    print(f"   First movie type: {type(first_movie)}")
                    if isinstance(first_movie, dict):
                        print(f"   Movie keys: {list(first_movie.keys())[:10]}...")  # Show first 10 keys
                
                return True
            else:
                print(f"   ❌ Failed to fetch movies: {response.status_code}")
                if response.status_code == 404:
                    print(f"   💡 Trying alternative movies endpoint...")
                    return self._fetch_movies_alternative(url, headers)
                return False
                
        except Exception as e:
            print(f"   ❌ Error fetching movies: {e}")
            return False
    
    def _fetch_series(self, url, headers):
        """Fetch TV series using Bazarr API"""
        try:
            # Use the correct series endpoint
            response = requests.get(f"{url}/api/series", headers=headers, timeout=30)
            print(f"   Series API response: {response.status_code}")
            
            if response.status_code == 200:
                series_data = response.json()
                
                # Handle both list and dict responses
                if isinstance(series_data, dict) and 'data' in series_data:
                    self.series = series_data['data']
                elif isinstance(series_data, list):
                    self.series = series_data
                else:
                    print(f"   ⚠️  Unexpected series data format: {type(series_data)}")
                    self.series = []
                
                print(f"   Found {len(self.series)} TV series in Bazarr")
                
                # Debug: Show structure of first series
                if self.series:
                    first_series = self.series[0]
                    print(f"   First series type: {type(first_series)}")
                    if isinstance(first_series, dict):
                        print(f"   Series keys: {list(first_series.keys())[:10]}...")  # Show first 10 keys
                
                return True
            else:
                print(f"   ❌ Failed to fetch series: {response.status_code}")
                if response.status_code == 404:
                    print(f"   💡 Trying alternative series endpoint...")
                    return self._fetch_series_alternative(url, headers)
                return False
                
        except Exception as e:
            print(f"   ❌ Error fetching series: {e}")
            return False
    
    def _fetch_movies_alternative(self, url, headers):
        """Try alternative movies endpoints"""
        alternative_endpoints = [
            "/api/movies/wanted",
            "/api/movies/history", 
            "/api/movies/blacklist"
        ]
        
        for endpoint in alternative_endpoints:
            try:
                print(f"   Trying endpoint: {endpoint}")
                response = requests.get(f"{url}{endpoint}", headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        print(f"   ✅ Alternative endpoint worked: {endpoint}")
                        self.movies = data if isinstance(data, list) else data.get('data', [])
                        return True
            except:
                continue
        
        print(f"   ❌ No working movies endpoint found")
        return False
    
    def _fetch_series_alternative(self, url, headers):
        """Try alternative series endpoints"""
        alternative_endpoints = [
            "/api/series/wanted",
            "/api/series/history",
            "/api/episodes"
        ]
        
        for endpoint in alternative_endpoints:
            try:
                print(f"   Trying endpoint: {endpoint}")
                response = requests.get(f"{url}{endpoint}", headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        print(f"   ✅ Alternative endpoint worked: {endpoint}")
                        self.series = data if isinstance(data, list) else data.get('data', [])
                        return True
            except:
                continue
        
        print(f"   ❌ No working series endpoint found")
        return False

    def get_movie_subtitles(self, movie_id):
        """Get subtitles for a specific movie"""
        try:
            url = self.credential_manager.bazarr_url
            headers = {'X-API-KEY': self.credential_manager.bazarr_api_key}
            
            response = requests.get(f"{url}/api/movies/{movie_id}/subtitles", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def get_series_subtitles(self, series_id):
        """Get subtitles for a specific series"""
        try:
            url = self.credential_manager.bazarr_url
            headers = {'X-API-KEY': self.credential_manager.bazarr_api_key}
            
            response = requests.get(f"{url}/api/series/{series_id}/subtitles", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def get_series_episodes(self, series_id):
        """Get episodes for a specific series"""
        try:
            url = self.credential_manager.bazarr_url
            headers = {'X-API-KEY': self.credential_manager.bazarr_api_key}
            
            # Try the series episodes endpoint
            response = requests.get(f"{url}/api/series/{series_id}/episodes", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            
            # Alternative: try episodes endpoint with series filter
            response = requests.get(f"{url}/api/episodes?seriesId={series_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
                
            return []
        except Exception as e:
            print(f"   Error fetching episodes: {e}")
            return []
    
    def get_wanted_movies(self):
        """
        Get movies that need subtitles from Bazarr's wanted list
        
        Uses Bazarr's /api/movies/wanted endpoint to fetch movies that are missing
        subtitles in the configured languages.
        
        Returns:
            list: List of movie dictionaries containing title, path, and metadata
                  Returns empty list if no movies need subtitles or on error
        """
        try:
            url = self.credential_manager.bazarr_url
            api_key = self.credential_manager.bazarr_api_key
            
            if not url or not api_key:
                print("⚠️ Bazarr credentials not configured")
                return []
            
            headers = {'X-API-KEY': api_key}
            print("🔍 Fetching wanted movies from Bazarr...")
            
            response = requests.get(f"{url}/api/movies/wanted", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                wanted_items = data if isinstance(data, list) else data.get('data', [])
                print(f"   Found {len(wanted_items)} movies needing subtitles")
                return wanted_items
            else:
                print(f"   ❌ Failed to fetch wanted movies: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error fetching wanted movies: {e}")
            return []
    
    def get_wanted_series(self):
        """
        Get TV series episodes that need subtitles from Bazarr's wanted list
        
        Uses Bazarr's /api/episodes/wanted endpoint to fetch TV episodes that are 
        missing subtitles in the configured languages.
        
        Returns:
            list: List of episode dictionaries containing seriesTitle, episodeTitle,
                  episode_number, and metadata. Returns empty list if no episodes 
                  need subtitles or on error
        """
        try:
            url = self.credential_manager.bazarr_url
            api_key = self.credential_manager.bazarr_api_key
            
            if not url or not api_key:
                print("⚠️ Bazarr credentials not configured")
                return []
            
            headers = {'X-API-KEY': api_key}
            print("🔍 Fetching wanted TV episodes from Bazarr...")
            
            # Use the correct endpoint for wanted episodes
            response = requests.get(f"{url}/api/episodes/wanted", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                wanted_items = data.get('data', []) if isinstance(data, dict) else data
                print(f"   Found {len(wanted_items)} TV episodes needing subtitles")
                return wanted_items
            else:
                print(f"   ❌ Failed to fetch wanted series: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error fetching wanted series: {e}")
            return []
    
    def get_all_wanted_items(self):
        """
        Get all items (movies + TV episodes) that need subtitles
        
        Combines results from both get_wanted_movies() and get_wanted_series()
        to provide a comprehensive list of all media needing subtitles.
        
        Returns:
            dict: Dictionary containing:
                - 'movies': List of movies needing subtitles
                - 'series': List of TV episodes needing subtitles  
                - 'total': Total count of items needing subtitles
        """
        print("🎯 Fetching all items needing subtitles...")
        
        wanted_movies = self.get_wanted_movies()
        wanted_series = self.get_wanted_series()
        
        total_wanted = len(wanted_movies) + len(wanted_series)
        print(f"📊 Total items needing subtitles: {total_wanted}")
        print(f"   Movies: {len(wanted_movies)}")
        print(f"   TV Episodes: {len(wanted_series)}")
        
        return {
            'movies': wanted_movies,
            'series': wanted_series,
            'total': total_wanted
        }