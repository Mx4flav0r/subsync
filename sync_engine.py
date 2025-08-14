#!/usr/bin/env python3
"""
Sync Engine Module
Core subtitle synchronization powered by your PathMapper
"""

import os
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import config
from database import database
from bazarr import bazarr

# Import your powerful PathMapper - THE CROWN JEWEL 🔥
try:
    from path_mapper import PathMapper
    print("✅ PathMapper imported successfully")
    PATH_MAPPER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import PathMapper: {e}")
    PathMapper = None
    PATH_MAPPER_AVAILABLE = False

try:
    from archive_manager import ArchiveManager
    print("✅ ArchiveManager imported successfully") 
    ARCHIVE_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import ArchiveManager: {e}")
    ArchiveManager = None
    ARCHIVE_MANAGER_AVAILABLE = False

@dataclass
class SyncResult:
    """Result of a sync operation"""
    success: bool
    message: str
    sync_time: float = 0.0
    output_path: str = ""
    method: str = ""
    offset: float = 0.0
    skipped: bool = False

class SyncEngine:
    """Core sync engine powered by your PathMapper 🔥"""
    
    def __init__(self):
        # Initialize your powerful PathMapper - THE CORE ENGINE
        if PATH_MAPPER_AVAILABLE and PathMapper:
            # Get bazarr client from the bazarr service
            bazarr_client = None
            if hasattr(bazarr, 'core_integration'):
                bazarr_client = bazarr.core_integration
            
            # Pass config to PathMapper for translation settings
            config_dict = None
            if hasattr(config, 'settings'):
                config_dict = config.settings
            elif hasattr(config, 'get_config'):
                config_dict = config.get_config()
            
            self.path_mapper = PathMapper(bazarr_client=bazarr_client, config=config_dict)
            self.use_pathmapper = True
            print("🔥 Sync engine powered by your PathMapper!")
        else:
            self.path_mapper = None
            self.use_pathmapper = False
            print("⚠️ PathMapper not available - using fallback sync")
        
        # Initialize archive manager
        if ARCHIVE_MANAGER_AVAILABLE and ArchiveManager and config.get("auto_archive"):
            self.archive_manager = ArchiveManager()
            # Connect archive manager to path mapper if both available
            if self.path_mapper:
                self.path_mapper.archive_manager = self.archive_manager
            print("📦 Archive manager initialized")
        else:
            self.archive_manager = None
            print("⚠️ Archive manager not available")
        
        # Sync configuration
        self.sync_config = config.get_sync_config()
        
        # Initialize Plex integration
        self.plex_client = None
        self._init_plex_client()
    
    def _init_plex_client(self):
        """Initialize Plex client for subtitle management"""
        try:
            # Check if Plex integration is enabled
            if not config.get("plex_integration", True):
                print("⚠️ Plex integration disabled in settings")
                return
                
            plex_url = config.get("plex_url")
            plex_token = config.get("plex_token")
            
            if plex_url and plex_token:
                from plex_client import PlexSubtitleManager
                self.plex_client = PlexSubtitleManager(plex_url, plex_token)
                print("🎬 Plex integration enabled")
            else:
                print("⚠️ Plex credentials not configured - integration disabled")
                
        except ImportError:
            print("⚠️ Plex client not available")
        except Exception as e:
            print(f"⚠️ Plex initialization error: {e}")
    
    def _set_plex_default_subtitle(self, video_path: str, synced_subtitle_path: str = None, series_title: str = None):
        """Set synced subtitle as default in Plex"""
        if not self.plex_client:
            return False
        
        try:
            print(f"🎬 Setting Plex default subtitle for: {os.path.basename(video_path)}")
            if series_title:
                print(f"📺 Series context: {series_title}")
            
            # Convert local path to Plex path for better matching
            try:
                from path_utils import convert_local_path_to_plex_path
                plex_video_path = convert_local_path_to_plex_path(video_path)
                print(f"🗺️ Path mapping: {video_path} → {plex_video_path}")
            except ImportError:
                # Fallback to original path if path_utils not available
                plex_video_path = video_path
                print(f"⚠️ Using original path (path_utils not available)")
            
            # Use the existing method in plex_client with the mapped path and series title
            success, message = self.plex_client.find_and_set_synced_subtitle(plex_video_path, series_title)
            
            if success:
                print(f"✅ Plex: {message}")
                return True
            else:
                print(f"⚠️ Plex: {message}")
                # Try with original path as fallback
                if plex_video_path != video_path:
                    print(f"🔄 Retrying with original path...")
                    success, message = self.plex_client.find_and_set_synced_subtitle(video_path)
                    if success:
                        print(f"✅ Plex (fallback): {message}")
                        return True
                return False
                
        except Exception as e:
            print(f"❌ Plex error: {e}")
            return False
    
    def sync_file(self, video_path: str, subtitle_path: str, 
                  language: str = "nl") -> SyncResult:
        """Sync a single subtitle file using PathMapper power 🔥"""
        
        if not self.use_pathmapper:
            return self._fallback_sync(video_path, subtitle_path, language)
        
        print(f"🎯 Syncing: {os.path.basename(video_path)}")
        print(f"📄 Subtitle: {os.path.basename(subtitle_path)}")
        
        try:
            # 🔥 Check if already synced using PathMapper's duplicate detection
            is_synced, last_sync, offset = self.path_mapper.is_file_already_synced(video_path, language)
            
            if is_synced:
                synced_path = self._get_synced_path(subtitle_path)
                if os.path.exists(synced_path):
                    return SyncResult(
                        success=True,
                        message=f"Already synced (last: {last_sync})",
                        output_path=synced_path,
                        skipped=True
                    )
            
            # 🔥 Use PathMapper's powerful sync method
            start_time = time.time()
            success, result_message = self.path_mapper.sync_using_simple_method(video_path, subtitle_path)
            sync_time = time.time() - start_time
            
            if success:
                synced_path = self._get_synced_path(subtitle_path)
                
                # 🔥 Record sync using PathMapper's tracking
                if hasattr(self.path_mapper, 'record_file_sync'):
                    self.path_mapper.record_file_sync(
                        media_path=video_path,
                        media_title=os.path.basename(video_path),
                        media_type='file',
                        subtitle_path=subtitle_path,
                        language=language,
                        status='success',
                        sync_time=sync_time,
                        offset=0  # Extract from result_message if available
                    )
                
                # 🎬 Set as default subtitle in Plex
                self._set_plex_default_subtitle(video_path, synced_path)
                
                return SyncResult(
                    success=True,
                    message=result_message,
                    sync_time=sync_time,
                    output_path=synced_path,
                    method="pathmapper_ffsubsync"
                )
            else:
                return SyncResult(
                    success=False,
                    message=result_message,
                    sync_time=sync_time
                )
                
        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Sync error: {str(e)}"
            )
    
    def sync_bazarr_movie(self, movie: Dict[str, Any], language: str = "nl") -> SyncResult:
        """Sync movie from Bazarr using PathMapper's hybrid power 🔥"""
        
        if not self.use_pathmapper:
            return SyncResult(False, "PathMapper not available")
        
        title = movie.get('title', 'Unknown')
        print(f"\n🎬 SYNCING MOVIE: {title}")
        print("=" * 60)
        
        try:
            # 🔥 Use PathMapper's powerful sync_movie_with_pathmapper method
            if hasattr(self.path_mapper, 'sync_movie_with_pathmapper'):
                result = self.path_mapper.sync_movie_with_pathmapper(movie, language)
            else:
                # Fallback to movie hybrid sync
                result_tuple = self.path_mapper.sync_movie_hybrid(movie, language)
                result = 'success' if result_tuple[0] else 'failed'
            
            if result == 'success':
                # 🎬 Try to set as default subtitle in Plex (if video path available)
                if 'path' in movie:
                    video_path = movie.get('path')
                    if self.path_mapper and hasattr(self.path_mapper, 'map_bazarr_path_to_local'):
                        local_video_path = self.path_mapper.map_bazarr_path_to_local(video_path)
                        if local_video_path:
                            self._set_plex_default_subtitle(local_video_path)
                
                return SyncResult(
                    success=True,
                    message="Movie synced successfully",
                    method="pathmapper_hybrid"
                )
            elif result == 'skipped':
                return SyncResult(
                    success=True,
                    message="Movie already synced",
                    skipped=True,
                    method="pathmapper_duplicate_detection"
                )
            else:
                return SyncResult(
                    success=False,
                    message=f"Movie sync failed: {result}",
                    method="pathmapper_failed"
                )
                
        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Movie sync error: {str(e)}"
            )
    
    def sync_bazarr_series(self, series: Dict[str, Any], language: str = "nl") -> SyncResult:
        """Sync TV series from Bazarr using PathMapper's hybrid power 🔥"""
        
        if not self.use_pathmapper:
            return SyncResult(False, "PathMapper not available")
        
        title = series.get('title', 'Unknown')
        series_path = series.get('path', '')
        
        print(f"\n📺 SYNCING SERIES: {title}")
        print("=" * 60)
        print(f"🔍 Series path: {series_path}")
        
        if not series_path:
            return SyncResult(False, "No series path provided")
        
        try:
            # Step 1: Map Bazarr series path to local path using PathMapper
            local_series_path = self.path_mapper.map_bazarr_path_to_local(series_path)
            
            if not local_series_path or not os.path.exists(local_series_path):
                return SyncResult(False, f"Local series path not found: {local_series_path}")
            
            print(f"🎯 Local series path: {local_series_path}")
            
            # Step 2: Find video files in the series directory
            video_files = self._find_video_files_in_series(local_series_path)
            
            if not video_files:
                return SyncResult(False, "No video files found in series")
            
            print(f"🎬 Found {len(video_files)} video files")
            
            # Step 3: Sync each episode using PathMapper
            success_count = 0
            skipped_count = 0
            failed_count = 0
            
            for i, video_file in enumerate(video_files, 1):
                episode_name = os.path.basename(video_file)
                print(f"\n📺 Episode {i}/{len(video_files)}: {episode_name}")
                
                # Check if episode already has synced subtitle and skip if so
                video_base = os.path.splitext(video_file)[0]
                potential_synced_files = [
                    f"{video_base}.{language}.synced.srt",
                    f"{video_base}.synced.{language}.srt", 
                    f"{video_base}.{language}.hi.synced.srt"
                ]
                
                synced_exists = False
                for synced_file in potential_synced_files:
                    if os.path.exists(synced_file):
                        print(f"   ✅ Already synced: {os.path.basename(synced_file)}")
                        skipped_count += 1
                        synced_exists = True
                        break
                
                if synced_exists:
                    continue
                
                # Find subtitle for this episode
                subtitle_file = self.path_mapper.find_matching_subtitle(video_file, language)
                
                if not subtitle_file:
                    print(f"   ❌ No {language} subtitle found")
                    failed_count += 1
                    continue
                
                # Check if already synced
                is_synced, synced_path = self.path_mapper.is_already_synced(video_file, subtitle_file)
                if is_synced and synced_path and os.path.exists(synced_path):
                    print(f"   ✅ Already synced: {os.path.basename(synced_path)}")
                    skipped_count += 1
                    continue
                
                # Sync using PathMapper's real implementation
                print(f"   🔄 Syncing subtitle...")
                success, message = self.path_mapper.sync_using_simple_method(video_file, subtitle_file)
                
                if success:
                    print(f"   ✅ Episode synced successfully!")
                    success_count += 1
                    
                    # 🎬 Set as default subtitle in Plex with series title context
                    self._set_plex_default_subtitle(video_file, series_title=title)
                else:
                    print(f"   ❌ Episode sync failed: {message}")
                    failed_count += 1
            
            # Return overall result
            total_processed = success_count + skipped_count + failed_count
            
            if success_count > 0:
                message = f"Series sync completed: {success_count} synced, {skipped_count} skipped, {failed_count} failed"
                return SyncResult(True, message, method="pathmapper_series_sync")
            elif skipped_count > 0:
                message = f"All episodes already synced: {skipped_count} episodes"
                return SyncResult(True, message, skipped=True, method="pathmapper_series_sync")
            else:
                message = f"Series sync failed: {failed_count} episodes failed"
                return SyncResult(False, message)
                
        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Series sync error: {str(e)}"
            )
    
    def batch_sync_movies(self, movies: List[Dict], language: str = "nl") -> Dict[str, int]:
        """Batch sync movies using PathMapper's session tracking 🔥"""
        
        if not movies:
            return {"successful": 0, "failed": 0, "skipped": 0}
        
        print(f"\n🎬 BATCH SYNC: {len(movies)} MOVIES")
        print("=" * 50)
        
        # 🔥 Start session tracking using PathMapper
        session_id = None
        if self.path_mapper and hasattr(self.path_mapper, 'start_sync_session'):
            session_id = self.path_mapper.start_sync_session('batch_movies', len(movies))
        
        results = {"successful": 0, "failed": 0, "skipped": 0}
        
        for i, movie in enumerate(movies, 1):
            title = movie.get('title', f'Movie {i}')
            print(f"\n🎬 {i}/{len(movies)}: {title}")
            
            result = self.sync_bazarr_movie(movie, language)
            
            if result.success:
                if result.skipped:
                    results["skipped"] += 1
                    print(f"   ⭐ Skipped: {result.message}")
                else:
                    results["successful"] += 1
                    print(f"   ✅ Success: {result.message}")
            else:
                results["failed"] += 1
                print(f"   ❌ Failed: {result.message}")
        
        # 🔥 End session tracking using PathMapper
        if session_id and self.path_mapper and hasattr(self.path_mapper, 'end_sync_session'):
            self.path_mapper.end_sync_session(session_id, results["successful"], results["failed"], results["skipped"])
        
        return results
    
    def batch_sync_series(self, series: List[Dict], language: str = "nl") -> Dict[str, int]:
        """Batch sync TV series using PathMapper's session tracking 🔥"""
        
        if not series:
            return {"successful": 0, "failed": 0, "skipped": 0}
        
        print(f"\n📺 BATCH SYNC: {len(series)} TV SERIES")
        print("=" * 50)
        
        # 🔥 Start session tracking using PathMapper
        session_id = None
        if self.path_mapper and hasattr(self.path_mapper, 'start_sync_session'):
            session_id = self.path_mapper.start_sync_session('batch_series', len(series))
        
        results = {"successful": 0, "failed": 0, "skipped": 0}
        
        for i, series_item in enumerate(series, 1):
            title = series_item.get('title', f'Series {i}')
            print(f"\n📺 {i}/{len(series)}: {title}")
            
            result = self.sync_bazarr_series(series_item, language)
            
            if result.success:
                if result.skipped:
                    results["skipped"] += 1
                    print(f"   ⭐ Skipped: {result.message}")
                else:
                    results["successful"] += 1
                    print(f"   ✅ Success: {result.message}")
            else:
                results["failed"] += 1
                print(f"   ❌ Failed: {result.message}")
        
        # 🔥 End session tracking using PathMapper
        if session_id and self.path_mapper and hasattr(self.path_mapper, 'end_sync_session'):
            self.path_mapper.end_sync_session(session_id, results["successful"], results["failed"], results["skipped"])
        
        return results
    
    def process_wanted_items_with_translation(self, language: str = "nl") -> Dict[str, int]:
        """
        Process items from Bazarr's wanted list and generate subtitles via translation 🎯
        
        This is the main function for automatic subtitle generation. It:
        1. Fetches items from Bazarr's wanted list (movies + TV episodes)
        2. Finds local file paths for each item
        3. Attempts to translate existing subtitles to target language
        4. Creates new subtitle files when successful
        
        Args:
            language (str): Target language code (default: "nl" for Dutch)
            
        Returns:
            dict: Results containing counts of successful, failed, skipped, and translated items
                - 'successful': Items processed successfully
                - 'failed': Items that failed processing
                - 'skipped': Items that were skipped
                - 'translated': Items where new subtitles were created via translation
                
        Prerequisites:
            - Bazarr integration must be available
            - Auto-translation must be enabled in config
            - PathMapper must be initialized with translation support
        """
        print(f"\n🎯 PROCESSING WANTED ITEMS WITH TRANSLATION")
        print("=" * 60)
        
        # Check if we have Bazarr integration
        if not self.use_pathmapper or not self.path_mapper or not self.path_mapper.bazarr_client:
            print("❌ Bazarr integration not available")
            return {"successful": 0, "failed": 0, "skipped": 0}
        
        # Check if translation is enabled
        if not self.path_mapper.config or not self.path_mapper.config.get('auto_translation', False):
            print("❌ Auto-translation is disabled")
            print("   Enable it in config: auto_translation = True")
            return {"successful": 0, "failed": 0, "skipped": 0}
        
        # Get wanted items from Bazarr
        wanted_data = self.path_mapper.bazarr_client.get_all_wanted_items()
        
        if wanted_data['total'] == 0:
            print("🎉 No items need subtitles - everything is up to date!")
            return {"successful": 0, "failed": 0, "skipped": 0}
        
        print(f"📊 Found {wanted_data['total']} items needing subtitles:")
        print(f"   Movies: {len(wanted_data['movies'])}")
        print(f"   TV Episodes: {len(wanted_data['series'])}")
        print()
        
        results = {"successful": 0, "failed": 0, "skipped": 0, "translated": 0}
        session_id = None
        
        # Start session tracking
        if self.path_mapper and hasattr(self.path_mapper, 'start_sync_session'):
            session_id = self.path_mapper.start_sync_session('wanted_translation', wanted_data['total'])
        
        # Process wanted movies
        for movie in wanted_data['movies']:
            try:
                print(f"\n🎬 Processing wanted movie: {movie.get('title', 'Unknown')}")
                
                # Try to find the movie file using path mapping
                movie_path = self._find_movie_path(movie)
                if not movie_path:
                    print(f"   ⚠️ Could not find movie file")
                    results["failed"] += 1
                    continue
                
                # Try to find and translate subtitles
                translated_path = self._process_wanted_item_translation(movie_path, language)
                
                if translated_path:
                    print(f"   ✅ Created Dutch subtitles via translation")
                    results["successful"] += 1
                    results["translated"] += 1
                else:
                    print(f"   ❌ Translation failed")
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"   ❌ Error processing movie: {e}")
                results["failed"] += 1
        
        # Process wanted TV episodes
        for episode in wanted_data['series']:
            try:
                series_title = episode.get('seriesTitle', 'Unknown Series')
                episode_title = episode.get('episodeTitle', 'Unknown Episode')
                episode_number = episode.get('episode_number', '?x?')
                print(f"\n📺 Processing wanted episode: {series_title} {episode_number} - {episode_title}")
                
                # Try to find the episode file
                episode_path = self._find_episode_path(episode)
                if not episode_path:
                    print(f"   ⚠️ Could not find episode file")
                    results["failed"] += 1
                    continue
                
                # Try to find and translate subtitles
                translated_path = self._process_wanted_item_translation(episode_path, language)
                
                if translated_path:
                    print(f"   ✅ Created Dutch subtitles via translation")
                    results["successful"] += 1
                    results["translated"] += 1
                else:
                    print(f"   ❌ Translation failed")
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"   ❌ Error processing episode: {e}")
                results["failed"] += 1
        
        # End session tracking
        if session_id and self.path_mapper and hasattr(self.path_mapper, 'end_sync_session'):
            self.path_mapper.end_sync_session(session_id, results["successful"], results["failed"], results["skipped"])
        
        print(f"\n📊 WANTED ITEMS PROCESSING COMPLETE")
        print(f"   ✅ Successfully translated: {results['translated']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   ⏭️ Skipped: {results['skipped']}")
        
        return results
    
    def _find_movie_path(self, movie_data: dict) -> str:
        """
        Find the actual file path for a movie from Bazarr data
        
        Attempts to locate the movie file using:
        1. Direct path mapping from Bazarr path data
        2. Fuzzy search by movie title across all movie directories
        
        Args:
            movie_data (dict): Movie data from Bazarr containing title, path, etc.
            
        Returns:
            str: Full path to movie file if found, None otherwise
        """
        try:
            # Try to get path from Bazarr data
            if 'path' in movie_data:
                bazarr_path = movie_data['path']
                # Use path mapper to convert from Plex path to local path
                if self.path_mapper:
                    local_path = self.path_mapper._map_plex_to_local(bazarr_path)
                    if local_path and os.path.exists(local_path):
                        return local_path
            
            # Fallback: search by title
            title = movie_data.get('title', '')
            if title:
                # Search in all movie directories
                for base_path in ["/Volumes/Data/Movies", "/Volumes/Data/Cartoons", "/Volumes/Data/Documentaries", "/Volumes/Data/Christmas", "/Volumes/Data/Dive"]:
                    if os.path.exists(base_path):
                        for item in os.listdir(base_path):
                            if title.lower() in item.lower():
                                movie_dir = os.path.join(base_path, item)
                                if os.path.isdir(movie_dir):
                                    # Find video file in directory
                                    for file in os.listdir(movie_dir):
                                        if file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
                                            return os.path.join(movie_dir, file)
            
            return None
            
        except Exception as e:
            print(f"   Error finding movie path: {e}")
            return None
    
    def _find_episode_path(self, episode_data: dict) -> str:
        """
        Find the actual file path for a TV episode from Bazarr data
        
        Searches for TV episode files using series title matching.
        Currently finds the first video file in matching series directory.
        
        Args:
            episode_data (dict): Episode data from Bazarr containing seriesTitle, 
                               episodeTitle, episode_number, etc.
            
        Returns:
            str: Full path to episode file if found, None otherwise
            
        TODO: Enhance to match exact episode using episode_number field
        """
        try:
            # Try to get path from Bazarr data - episodes/wanted doesn't seem to include direct paths
            # We'll need to use Sonarr IDs or search by series title
            
            # Get series information
            series_title = episode_data.get('seriesTitle', '')
            episode_number = episode_data.get('episode_number', '')  # Format like "1x49"
            sonarr_series_id = episode_data.get('sonarrSeriesId')
            sonarr_episode_id = episode_data.get('sonarrEpisodeId')
            
            if series_title:
                series_base = "/Volumes/Data/TVShows"
                if os.path.exists(series_base):
                    # Search for series directory by title
                    for series_dir in os.listdir(series_base):
                        if series_title.lower() in series_dir.lower():
                            series_path = os.path.join(series_base, series_dir)
                            if os.path.isdir(series_path):
                                # For now, just return the first video file found
                                # TODO: Improve this to match exact episode using episode_number
                                for root, dirs, files in os.walk(series_path):
                                    for file in files:
                                        if file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
                                            return os.path.join(root, file)
            
            return None
            
        except Exception as e:
            print(f"   Error finding episode path: {e}")
            return None
    
    def _process_wanted_item_translation(self, video_path: str, target_language: str) -> str:
        """
        Process a single wanted item for translation
        
        Checks if target language subtitles already exist, and if not,
        attempts to create them via translation using SubtitleTranslator.
        
        Args:
            video_path (str): Full path to video file
            target_language (str): Target language code (e.g., "nl")
            
        Returns:
            str: Path to subtitle file if successful (existing or newly created), 
                 None if translation failed
        """
        try:
            # Check if we already have the target language subtitles
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            
            # Look for existing target language subtitles
            target_subtitle = os.path.join(video_dir, f"{video_name}.{target_language}.srt")
            if os.path.exists(target_subtitle):
                print(f"   ✅ Target language subtitles already exist")
                return target_subtitle
            
            # Use subtitle translator to find and translate existing subtitles
            if hasattr(self.path_mapper, 'subtitle_translator'):
                translator = self.path_mapper.subtitle_translator
                translated_path = translator.find_and_translate_subtitles(video_path, target_language)
                
                if translated_path:
                    print(f"   🌍 Translated subtitles created: {os.path.basename(translated_path)}")
                    return translated_path
            
            return None
            
        except Exception as e:
            print(f"   Error during translation: {e}")
            return None

    def batch_sync_all(self, language: str = "nl") -> Dict[str, int]:
        """Batch sync all media using PathMapper's enhanced bulk sync 🔥"""
        
        # Get media from Bazarr
        movies, series = bazarr.get_all_media()
        total_items = len(movies) + len(series)
        
        if total_items == 0:
            print("❌ No media found")
            return {"successful": 0, "failed": 0, "skipped": 0}
        
        print(f"\n🚀 ENHANCED BULK SYNC - ALL MEDIA")
        print("=" * 60)
        print(f"📊 Total items to process:")
        print(f"   Movies: {len(movies)}")
        print(f"   TV Series: {len(series)}")
        print(f"   Total: {total_items}")
        print()
        print("✨ PATHMAPPER ENHANCED FEATURES:")
        print("   🔍 Duplicate detection (skip already synced)")
        print("   📊 Performance tracking and statistics")
        print("   📦 Automatic backup before sync")
        print("   🔄 Multiple VAD method fallbacks")
        print("   💾 Session tracking and reporting")
        
        # 🔥 Start PathMapper session tracking
        session_id = None
        if self.path_mapper and hasattr(self.path_mapper, 'start_sync_session'):
            session_id = self.path_mapper.start_sync_session('bulk_all', total_items)
        
        results = {"successful": 0, "failed": 0, "skipped": 0}
        
        # Process movies
        if movies:
            movie_results = self.batch_sync_movies(movies, language)
            for key in results:
                results[key] += movie_results[key]
        
        # Process series
        if series:
            series_results = self.batch_sync_series(series, language)
            for key in results:
                results[key] += series_results[key]
        
        # 🔥 End session tracking using PathMapper
        if session_id and self.path_mapper and hasattr(self.path_mapper, 'end_sync_session'):
            self.path_mapper.end_sync_session(session_id, results["successful"], results["failed"], results["skipped"])
        
        print(f"\n✅ ENHANCED BULK SYNC COMPLETE!")
        print(f"   ✅ Successful: {results['successful']}")
        print(f"   ⭐ Skipped (already synced): {results['skipped']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📊 Session {session_id} data saved for analysis")
        
        return results
    
    def parallel_sync(self, items: List[Dict], language: str = "nl", 
                     max_workers: int = None) -> Dict[str, int]:
        """Parallel sync using ThreadPoolExecutor (advanced feature) 🔥"""
        
        if not max_workers:
            max_workers = config.get("max_workers", 2)
        
        print(f"\n⚡ PARALLEL SYNC: {len(items)} items with {max_workers} workers")
        print("=" * 60)
        
        results = {"successful": 0, "failed": 0, "skipped": 0}
        
        def sync_item(item):
            """Sync a single item"""
            media_type = item.get('type', 'unknown')
            if 'episodes' in item or media_type == 'series':
                return self.sync_bazarr_series(item, language)
            else:
                return self.sync_bazarr_movie(item, language)
        
        # 🔥 Start session tracking using PathMapper
        session_id = None
        if self.path_mapper and hasattr(self.path_mapper, 'start_sync_session'):
            session_id = self.path_mapper.start_sync_session('parallel_sync', len(items))
        
        # Execute parallel sync
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_item = {executor.submit(sync_item, item): item for item in items}
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_item), 1):
                item = future_to_item[future]
                title = item.get('title', f'Item {i}')
                
                try:
                    result = future.result()
                    
                    if result.success:
                        if result.skipped:
                            results["skipped"] += 1
                            print(f"⭐ {i}/{len(items)} Skipped: {title}")
                        else:
                            results["successful"] += 1
                            print(f"✅ {i}/{len(items)} Success: {title}")
                    else:
                        results["failed"] += 1
                        print(f"❌ {i}/{len(items)} Failed: {title}")
                        
                except Exception as e:
                    results["failed"] += 1
                    print(f"❌ {i}/{len(items)} Error: {title} - {e}")
        
        # 🔥 End session tracking using PathMapper
        if session_id and self.path_mapper and hasattr(self.path_mapper, 'end_sync_session'):
            self.path_mapper.end_sync_session(session_id, results["successful"], results["failed"], results["skipped"])
        
        return results
    
    def get_sync_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get sync statistics using PathMapper's tracking 🔥"""
        if self.path_mapper and hasattr(self.path_mapper, 'get_sync_statistics'):
            return self.path_mapper.get_sync_statistics(days)
        else:
            # Fallback to database statistics
            return database.get_statistics(days)
    
    def show_sync_statistics(self, days: int = 7):
        """Display comprehensive sync statistics using PathMapper 🔥"""
        if self.path_mapper and hasattr(self.path_mapper, 'show_sync_statistics'):
            self.path_mapper.show_sync_statistics()
        else:
            # Fallback implementation
            stats = self.get_sync_statistics(days)
            
            print(f"\n📊 SYNC STATISTICS (Last {days} days)")
            print("=" * 50)
            
            if stats.get('overall'):
                total, successful, failed, avg_time, max_time, min_time = stats['overall']
                success_rate = (successful / total * 100) if total > 0 else 0
                
                print(f"📈 Overall Performance:")
                print(f"   Total syncs: {total}")
                print(f"   Successful: {successful} ({success_rate:.1f}%)")
                print(f"   Failed: {failed}")
                print(f"   Average time: {avg_time:.1f}s")
                print(f"   Fastest: {min_time:.1f}s")
                print(f"   Slowest: {max_time:.1f}s")
                
                if stats.get('by_language'):
                    print(f"\n🌍 By Language:")
                    for language, count, successful in stats['by_language']:
                        rate = (successful / count * 100) if count > 0 else 0
                        print(f"   {language}: {count} total, {successful} successful ({rate:.1f}%)")
            else:
                print("📭 No statistics available")
    
    def _fallback_sync(self, video_path: str, subtitle_path: str, language: str) -> SyncResult:
        """Fallback sync implementation when PathMapper not available"""
        try:
            import subprocess
            import shutil
            
            # Create backup
            backup_path = f"{subtitle_path}.backup"
            if not os.path.exists(backup_path):
                shutil.copy2(subtitle_path, backup_path)
            
            # Create output path
            synced_path = self._get_synced_path(subtitle_path)
            
            # Run ffsubsync
            cmd = [
                'ffsubsync', video_path,
                '-i', subtitle_path,
                '-o', synced_path
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            sync_time = time.time() - start_time
            
            if result.returncode == 0 and os.path.exists(synced_path):
                # Record in database
                database.record_sync(video_path, subtitle_path, synced_path, language, "success", sync_time)
                
                return SyncResult(
                    success=True,
                    message=f"Synced in {sync_time:.1f}s",
                    sync_time=sync_time,
                    output_path=synced_path,
                    method="fallback_ffsubsync"
                )
            else:
                return SyncResult(
                    success=False,
                    message=f"ffsubsync failed: {result.stderr[:100]}",
                    sync_time=sync_time
                )
                
        except Exception as e:
            return SyncResult(
                success=False,
                message=f"Fallback sync error: {str(e)}"
            )
    
    def _get_synced_path(self, subtitle_path: str) -> str:
        """Get the path for synced subtitle"""
        base_path = os.path.splitext(subtitle_path)[0]
        return f"{base_path}.synced.srt"
    
    def health_check(self) -> Dict[str, Any]:
        """Check sync engine health"""
        health = {
            "pathmapper_available": self.use_pathmapper,
            "archive_manager_available": self.archive_manager is not None,
            "bazarr_connected": bazarr.test_connection() if bazarr.is_configured() else False,
            "database_healthy": True,
            "config_loaded": True
        }
        
        # Test database
        try:
            database.health_check()
        except:
            health["database_healthy"] = False
        
        # Test config
        try:
            config.get("preferred_languages")
        except:
            health["config_loaded"] = False
        
        return health
    
    def _find_video_files_in_series(self, series_path: str) -> List[str]:
        """Find all video files in a TV series directory"""
        video_files = []
        video_extensions = ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.m4v']
        
        try:
            # Walk through all subdirectories to find video files
            for root, dirs, files in os.walk(series_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in video_extensions):
                        video_path = os.path.join(root, file)
                        video_files.append(video_path)
            
            # Sort by filename for consistent ordering
            video_files.sort(key=lambda x: os.path.basename(x).lower())
            
        except Exception as e:
            print(f"   ⚠️ Error finding video files: {e}")
        
        return video_files

# Global sync engine instance
sync_engine = SyncEngine()
