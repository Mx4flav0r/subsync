#!/usr/bin/env python3
"""Test Plex search functionality"""

from plex_client import PlexSubtitleManager
import config

def test_plex_search():
    try:
        print("🧪 TESTING PLEX SEARCH")
        print("="*50)
        
        # Load configuration
        config_obj = config.Config()
        
        # Test Plex connection and search
        plex_client = PlexSubtitleManager(
            plex_url=config_obj.get('plex_url', 'http://192.168.90.3:32400'),
            plex_token=config_obj.get('plex_token', '')
        )
        
        # Test connection first
        print("🔗 Testing Plex connection...")
        if plex_client.test_connection():
            print("✅ Plex connection successful")
        else:
            print("❌ Plex connection failed")
            return
        
        # Test the search specifically
        video_path = '/PlexMedia/Movies/A Dogs Journey (2019)/A.Dogs.Journey.2019.1080p.WEB-DL.DD5.1.H264-FGT NL subs.A.mkv'
        print(f"\n🔍 Testing search for: {video_path}")
        
        # Test just the search method
        media_item = plex_client.search_media_by_path(video_path)
        
        if media_item:
            print(f"✅ Found media: {media_item['title']}")
            print(f"   Rating Key: {media_item['rating_key']}")
            print(f"   File Path: {media_item['file_path']}")
        else:
            print("❌ No media found")
            
            # Let's also test manual title searches
            print("\n🔍 Manual title testing...")
            test_titles = [
                "A Dog's Journey",
                "A Dogs Journey", 
                "Dog's Journey",
                "Dogs Journey"
            ]
            
            libraries = plex_client.get_libraries()
            movie_libs = [lib for lib in libraries if lib['type'] == 'movie']
            
            for lib in movie_libs:
                print(f"\n📚 Testing in library: {lib['title']}")
                for title in test_titles:
                    print(f"   🔍 Searching for: '{title}'")
                    matches = plex_client._search_library_by_term(lib['key'], title)
                    if matches:
                        print(f"   ✅ Found: {matches[0]['title']}")
                        break
                    else:
                        print(f"   ❌ Not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_plex_search()
