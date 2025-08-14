#!/usr/bin/env python3
"""
Test Path Mapping System
"""

from config import config
from path_utils import *

def test_path_mapping():
    """Test the new path mapping system"""
    print("🗺️ TESTING PATH MAPPING SYSTEM")
    print("=" * 50)
    
    # Show current environment
    summary = get_environment_summary()
    print(f"📍 Environment: {summary['environment']}")
    print(f"📝 Description: {summary['description']}")
    print()
    
    # Show paths
    print("🛤️ CONFIGURED PATHS:")
    paths = summary['paths']
    for key, value in paths.items():
        if key != 'description':
            print(f"   {key}: {value}")
    print()
    
    # Test path validation
    print("🧪 PATH VALIDATION:")
    validation = summary['validation']
    for path_type, is_valid in validation.items():
        status = "✅" if is_valid else "❌" if is_valid is False else "⚠️"
        print(f"   {path_type}: {status}")
    print()
    
    # Test path conversion
    print("🔄 PATH CONVERSION TESTS:")
    test_paths = [
        "/Volumes/Data/Movies/SomeMovie/movie.mkv",
        "/Volumes/Data/TVShows/SomeSeries/Season 1/episode.mkv"
    ]
    
    for local_path in test_paths:
        plex_path = convert_local_path_to_plex_path(local_path)
        back_to_local = convert_plex_path_to_local_path(plex_path)
        
        print(f"   Local:  {local_path}")
        print(f"   Plex:   {plex_path}")
        print(f"   Back:   {back_to_local}")
        print(f"   Match:  {'✅' if local_path == back_to_local else '❌'}")
        print()

if __name__ == "__main__":
    test_path_mapping()
