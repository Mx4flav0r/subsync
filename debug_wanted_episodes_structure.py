#!/usr/bin/env python3
"""
Debug the actual data structure returned by Bazarr's episodes/wanted API
"""

import requests
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from credential_manager import CredentialManager
from database_manager import DatabaseManager

def debug_wanted_episodes_data():
    """Debug the actual structure of wanted episodes data"""
    try:
        # Initialize components
        db_manager = DatabaseManager()
        cred_manager = CredentialManager(db_manager)
        
        url = cred_manager.bazarr_url
        api_key = cred_manager.bazarr_api_key
        
        if not url or not api_key:
            print("❌ Bazarr credentials not configured")
            return
        
        headers = {'X-API-KEY': api_key}
        print(f"🔍 Fetching wanted episodes data from: {url}/api/episodes/wanted")
        
        # Get wanted episodes with a limit to see structure
        response = requests.get(f"{url}/api/episodes/wanted?length=5", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Response received")
            print(f"   Response type: {type(data)}")
            print(f"   Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict) and 'data' in data:
                episodes = data['data']
                total = data.get('total', len(episodes))
                
                print(f"\n📊 Episodes data:")
                print(f"   Total episodes needing subtitles: {total}")
                print(f"   Episodes in this response: {len(episodes)}")
                
                if episodes:
                    print(f"\n🔍 First episode structure:")
                    first_episode = episodes[0]
                    print(f"   Keys available: {list(first_episode.keys())}")
                    
                    print(f"\n📝 Sample episode data:")
                    for key, value in first_episode.items():
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"   {key}: {value}")
                    
                    print(f"\n📺 Sample episodes formatted:")
                    for i, episode in enumerate(episodes[:3]):
                        print(f"\n   Episode {i+1}:")
                        
                        # Try different possible field names for series title
                        series_title = (episode.get('seriesTitle') or 
                                      episode.get('series_title') or 
                                      episode.get('series') or 
                                      episode.get('title') or 
                                      episode.get('seriesName') or
                                      'Unknown Series')
                        
                        # Try different possible field names for episode title
                        episode_title = (episode.get('episodeTitle') or 
                                       episode.get('episode_title') or 
                                       episode.get('episodeName') or
                                       episode.get('name') or
                                       'Unknown Episode')
                        
                        # Try to get season/episode numbers
                        season = episode.get('season', episode.get('seasonNumber', '?'))
                        episode_num = episode.get('episode', episode.get('episodeNumber', '?'))
                        
                        print(f"     Series: {series_title}")
                        print(f"     Episode: {episode_title}")
                        print(f"     Season: {season}")
                        print(f"     Episode #: {episode_num}")
                        
                        # Check if there's a path
                        path = episode.get('path', episode.get('episodePath', 'No path'))
                        print(f"     Path: {path}")
            
            else:
                print("❌ Unexpected data structure")
                print(f"Raw data: {json.dumps(data, indent=2)[:500]}...")
                
        else:
            print(f"❌ Failed to fetch wanted episodes: {response.status_code}")
            print(f"Error: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error debugging wanted episodes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_wanted_episodes_data()
