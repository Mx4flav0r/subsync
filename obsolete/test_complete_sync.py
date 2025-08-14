#!/usr/bin/env python3
"""Test complete movie sync with Plex integration"""

from sync_engine import SyncEngine
import config

def test_complete_sync():
    try:
        print('🎬 Testing complete movie sync with Plex integration...')

        # Initialize sync engine
        sync_engine = SyncEngine()

        # Test sync with the movie we know exists
        movie_data = {
            'title': "A Dog's Journey",
            'path': '/PlexMedia/Movies/A Dogs Journey (2019)/A.Dogs.Journey.2019.1080p.WEB-DL.DD5.1.H264-FGT NL subs.A.mkv',
            'radarrId': 123
        }

        print(f'📁 Testing with: {movie_data["path"]}')

        # Run the sync (this should now work with Plex integration)
        result = sync_engine.sync_bazarr_movie(
            movie=movie_data,
            language="nl"
        )

        print(f'🎯 Sync result: {result}')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_sync()
