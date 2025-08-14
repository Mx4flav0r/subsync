#!/usr/bin/env python3
"""
Test Multiple Movie Libraries Support
Tests the updated path mapping and Plex library discovery for multiple movie folders
"""

import sys
import os

# Add current directory to path for imports
sys.path.append('.')

from path_mapper import PathMapper
from plex_client import PlexSubtitleManager
from config import Config

def test_path_mappings():
    """Test that all movie library paths are properly mapped"""
    print("🧪 TESTING PATH MAPPINGS")
    print("=" * 50)
    
    # Create a mock bazarr client for PathMapper
    class MockBazarrClient:
        pass
    
    # Initialize PathMapper
    path_mapper = PathMapper(MockBazarrClient())
    
    # Test paths from different movie libraries (as they come from Bazarr)
    # Bazarr provides paths like /PlexMedia/[Folder], which get mapped to /Volumes/Data/[Folder]
    test_paths = [
        "/PlexMedia/Movies/Some Movie (2023)/movie.mkv",
        "/PlexMedia/Cartoons/Some Cartoon (2023)/cartoon.mkv", 
        "/PlexMedia/Documentaries/Some Doc (2023)/doc.mkv",
        "/PlexMedia/Christmas/Holiday Movie (2023)/holiday.mkv"
    ]
    
    print("📁 Testing Bazarr → Local path mappings:")
    print("   💡 Bazarr provides /PlexMedia/* paths, we map them to /Volumes/Data/*")
    for plex_path in test_paths:
        # Test mapping from Plex path to local path
        for server_path, local_path in path_mapper.path_mappings.items():
            if plex_path.startswith(server_path):
                mapped_path = plex_path.replace(server_path, local_path)
                print(f"   ✅ {plex_path}")
                print(f"      → {mapped_path}")
                
                # Check if directory exists
                base_dir = mapped_path.split('/')[:-1]  # Remove filename
                base_dir_path = '/'.join(base_dir)
                if os.path.exists(base_dir_path):
                    print(f"      📂 Base directory exists: {base_dir_path}")
                else:
                    print(f"      ❌ Base directory missing: {base_dir_path}")
                break
        else:
            print(f"   ❌ No mapping found for: {plex_path}")
    
    print(f"\n📚 Local search paths configured: {len(path_mapper.local_search_paths)}")
    for path in path_mapper.local_search_paths:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"   {exists} {path}")

def test_plex_libraries():
    """Test Plex library discovery"""
    print("\n🎬 TESTING PLEX LIBRARY DISCOVERY")
    print("=" * 50)
    
    try:
        config = Config()
        plex_url = config.get('plex_url', 'http://192.168.90.3:32400')
        plex_token = config.get('plex_token', '')
        
        if not plex_token:
            print("⚠️ No Plex token configured, skipping Plex tests")
            return
            
        plex_client = PlexSubtitleManager(plex_url, plex_token)
        
        # Get all libraries
        libraries = plex_client.get_libraries()
        movie_libraries = [lib for lib in libraries if lib['type'] == 'movie']
        
        print(f"📚 Found {len(movie_libraries)} movie libraries in Plex:")
        for lib in movie_libraries:
            print(f"   🎬 {lib['title']} (Key: {lib['key']})")
            
        # Expected movie library names - using Dutch translations as they appear in Plex
        # Note: These should match your actual Plex library names in Dutch
        expected_names_english = ['Movies', 'Cartoons', 'Documentaries', 'Christmas']
        possible_dutch_names = [
            'Films', 'Movies',  # Movies
            'Tekenfilms', 'Cartoons', 'Animatie',  # Cartoons  
            'Documentaires', 'Documentaries',  # Documentaries
            'Kerst', 'Christmas', 'Kerstfilms'  # Christmas
        ]
        
        found_names = [lib['title'] for lib in movie_libraries]
        
        print(f"\n🔍 All Plex Movie Libraries Found:")
        for lib in movie_libraries:
            print(f"   📽️ '{lib['title']}' (Key: {lib['key']})")
        
        print(f"\n🔍 Checking for expected content types:")
        print("   💡 Note: Library names should match your Dutch Plex setup")
        
        # Check if we have at least the expected number of movie libraries
        if len(movie_libraries) >= 4:
            print(f"   ✅ Found {len(movie_libraries)} movie libraries (expected ~4)")
        else:
            print(f"   ⚠️ Found {len(movie_libraries)} movie libraries (expected ~4)")
            print("      💡 Make sure all your movie folders are configured as Plex libraries")
                
    except Exception as e:
        print(f"❌ Error testing Plex libraries: {e}")
        print("💡 Make sure Plex is running and credentials are configured")

def test_config():
    """Test configuration settings"""
    print("\n⚙️ TESTING CONFIGURATION")
    print("=" * 50)
    
    config = Config()
    
    # Test base paths
    base_paths = config.get('base_paths', [])
    print(f"📁 Base paths configured: {len(base_paths)}")
    for path in base_paths:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"   {exists} {path}")
    
    # Test path mappings
    path_mappings = config.get('path_mappings', {})
    print(f"\n🗺️ Path mappings configured: {len(path_mappings)}")
    for plex_path, local_path in path_mappings.items():
        local_exists = "✅" if os.path.exists(local_path) else "❌"
        print(f"   {local_exists} {plex_path} → {local_path}")

def test_bazarr_paths():
    """Test what paths Bazarr actually returns"""
    print("\n🎯 TESTING BAZARR PATH FORMAT")
    print("=" * 50)
    
    try:
        from bazarr import BazarrIntegration
        from credential_manager import CredentialManager
        
        # Get credentials
        cred_manager = CredentialManager()
        bazarr_url, bazarr_api_key = cred_manager.get_bazarr_credentials()
        
        if not bazarr_url or not bazarr_api_key:
            print("⚠️ No Bazarr credentials configured, skipping Bazarr path test")
            return
            
        bazarr = BazarrIntegration(bazarr_url, bazarr_api_key)
        
        # Get some movies to see what paths look like
        print("📽️ Fetching sample movies from Bazarr...")
        movies = bazarr.get_movies()
        
        if movies:
            print(f"📊 Found {len(movies)} movies in Bazarr")
            print("\n📁 Sample movie paths from Bazarr:")
            
            # Show first few movie paths to see the format
            for i, movie in enumerate(movies[:5]):
                title = movie.get('title', 'Unknown')
                path = movie.get('path', 'No path')
                print(f"   {i+1}. {title}")
                print(f"      📂 Path: {path}")
                
                # Check if this path matches our mapping patterns
                for server_path in ['/PlexMedia/Movies', '/PlexMedia/Cartoons', '/PlexMedia/Documentaries', '/PlexMedia/Christmas']:
                    if path.startswith(server_path):
                        print(f"      ✅ Matches mapping pattern: {server_path}")
                        break
                else:
                    print(f"      ⚠️ Path doesn't match expected /PlexMedia/* pattern")
                print()
        else:
            print("❌ No movies found in Bazarr")
            
    except Exception as e:
        print(f"❌ Error testing Bazarr paths: {e}")
        print("💡 Make sure Bazarr is running and credentials are configured")

if __name__ == "__main__":
    print("🚀 TESTING MULTIPLE MOVIE LIBRARIES SUPPORT")
    print("=" * 60)
    
    test_config()
    test_path_mappings()
    test_bazarr_paths()
    test_plex_libraries()
    
    print("\n" + "=" * 60)
    print("✅ Testing complete! Check results above for any issues.")
