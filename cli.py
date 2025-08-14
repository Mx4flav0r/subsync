#!/usr/bin/env python3
"""
Command Line Interface Module
Clean, organized CLI for the subtitle sync system
"""

import os
import sys
from typing import Dict, List, Any, Optional

from config import config
from database import database
from bazarr import bazarr
from sync_engine import sync_engine

class SubtitleSyncCLI:
    """Clean command line interface for subtitle sync"""
    
    def __init__(self):
        self.running = True
        print("🚀 Subtitle Sync System Initialized")
        print("💪 Powered by PathMapper Engine")
    
    def run(self):
        """Main application loop"""
        try:
            # Health check
            self._startup_checks()
            
            while self.running:
                self._show_main_menu()
                try:
                    choice = input("\n👉 Enter choice (1-9): ").strip()
                    self._handle_main_choice(choice)
                except EOFError:
                    # Handle end of input stream gracefully
                    print("\n\n👋 Input stream ended. Goodbye!")
                    break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
    
    def _startup_checks(self):
        """Perform startup health checks"""
        print("\n🔍 STARTUP CHECKS")
        print("=" * 40)
        
        # Check PathMapper availability
        if sync_engine.use_pathmapper:
            print("✅ PathMapper engine loaded")
        else:
            print("⚠️ PathMapper not available - using fallback")
        
        # Check Bazarr configuration
        if bazarr.is_configured():
            if bazarr.test_connection():
                print("✅ Bazarr connected")
            else:
                print("❌ Bazarr connection failed")
                if input("Configure Bazarr now? (y/N): ").lower() == 'y':
                    bazarr.configure_credentials()
        else:
            print("⚠️ Bazarr not configured")
            if input("Configure Bazarr now? (y/N): ").lower() == 'y':
                bazarr.configure_credentials()
        
        # Check database
        health = database.health_check()
        if health.get("database_file") and health.get("writable"):
            print("✅ Database ready")
        else:
            print("⚠️ Database issues detected")
        
        print("✅ Startup complete!")
    
    def _show_main_menu(self):
        """Display main menu"""
        print("\n" + "="*70)
        print("🎯 SUBTITLE SYNC SYSTEM - MAIN MENU")
        print("="*70)
        print("1. 🎬 Sync Movies from Bazarr")
        print("2. 📺 Sync TV Series from Bazarr")
        print("3. 🚀 Bulk Sync ALL Media")
        print("4. 🎯 Process Wanted Items (Auto-Translate)")
        print("5. 📊 Statistics & Reports")
        print("6. ⚙️  Settings & Configuration")
        print("7. 📦 Archive Management")
        print("8. 🔧 System Tools")
        print("9. ❓ Help & Status")
        print("0. 🚪 Exit")
        print("="*70)
    
    def _handle_main_choice(self, choice: str):
        """Handle main menu choice"""
        handlers = {
            "1": self._movies_menu,
            "2": self._series_menu,
            "3": self._bulk_sync_menu,
            "4": self._wanted_items_menu,
            "5": self._statistics_menu,
            "6": self._settings_menu,
            "7": self._archive_menu,
            "8": self._tools_menu,
            "9": self._help_menu,
            "0": self._exit
        }
        
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            print("❌ Invalid choice. Please enter 0-9.")
    
    # =============================================================================
    # SYNC MENUS
    # =============================================================================
    
    def _movies_menu(self):
        """Movies sync menu"""
        print("\n🎬 MOVIE SYNC MENU")
        print("=" * 50)
        
        # Fetch movies
        movies = bazarr.get_movies()
        if not movies:
            print("❌ No movies found in Bazarr")
            if not bazarr.is_configured():
                print("💡 Configure Bazarr in Settings first")
            return
        
        print(f"📊 Found {len(movies)} movies in Bazarr")
        print("\nOptions:")
        print("1. Sync ALL movies")
        print("2. Browse and select movies")
        print("3. Search for specific movie")
        print("4. Quick sync (movies with Dutch subtitles)")
        print("5. Back to main menu")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            self._sync_all_movies(movies)
        elif choice == "2":
            self._browse_movies(movies)
        elif choice == "3":
            self._search_movies(movies)
        elif choice == "4":
            self._quick_sync_movies(movies)
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")
    
    def _series_menu(self):
        """TV series sync menu"""
        print("\n📺 TV SERIES SYNC MENU")
        print("=" * 50)
        
        # Fetch series
        series = bazarr.get_series()
        if not series:
            print("❌ No TV series found in Bazarr")
            if not bazarr.is_configured():
                print("💡 Configure Bazarr in Settings first")
            return
        
        print(f"📊 Found {len(series)} series in Bazarr")
        print("\nOptions:")
        print("1. Sync ALL series")
        print("2. Browse and select series")
        print("3. Search for specific series")
        print("4. Quick sync (series with Dutch subtitles)")
        print("5. Back to main menu")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            self._sync_all_series(series)
        elif choice == "2":
            self._browse_series(series)
        elif choice == "3":
            self._search_series(series)
        elif choice == "4":
            self._quick_sync_series(series)
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")
    
    def _bulk_sync_menu(self):
        """Bulk sync menu"""
        print("\n🚀 BULK SYNC MENU")
        print("=" * 50)
        
        movies, series = bazarr.get_all_media()
        total = len(movies) + len(series)
        
        if total == 0:
            print("❌ No media found in Bazarr")
            return
        
        print(f"📊 Available media:")
        print(f"   Movies: {len(movies)}")
        print(f"   TV Series: {len(series)}")
        print(f"   Total: {total}")
        print()
        print("Bulk sync options:")
        print("1. Sync ALL media (movies + series)")
        print("2. Sync movies only")
        print("3. Sync series only")
        print("4. Parallel sync (advanced)")
        print("5. Back to main menu")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            self._bulk_sync_all()
        elif choice == "2":
            self._bulk_sync_movies_only(movies)
        elif choice == "3":
            self._bulk_sync_series_only(series)
        elif choice == "4":
            self._parallel_sync_menu(movies + series)
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")
    
    def _wanted_items_menu(self):
        """
        Wanted items processing menu with automatic translation
        
        This menu provides access to the intelligent subtitle generation system
        that leverages Bazarr's "wanted" API to target only items missing subtitles.
        
        Features:
        - Displays preview of all items needing subtitles
        - Shows sample movies and TV episodes before processing  
        - Provides options for targeted processing (all, movies only, TV only)
        - Automatic translation from existing subtitles in other languages
        - Real-time progress feedback during processing
        
        Prerequisites:
        - PathMapper must be available
        - Auto-translation must be enabled in configuration
        - Bazarr integration must be functional
        """
        print("\n🎯 WANTED ITEMS PROCESSING MENU")
        print("=" * 50)
        print("This feature processes items from Bazarr's 'wanted' list")
        print("and automatically generates Dutch subtitles via translation.")
        print()
        
        # Check if translation is enabled
        if not sync_engine.use_pathmapper or not sync_engine.path_mapper:
            print("❌ PathMapper not available")
            return
        
        if not sync_engine.path_mapper.config or not sync_engine.path_mapper.config.get('auto_translation', False):
            print("❌ Auto-translation is disabled")
            print("   Enable it in Settings & Configuration menu")
            return
        
        # Get wanted items preview
        try:
            if hasattr(sync_engine.path_mapper, 'bazarr_client') and sync_engine.path_mapper.bazarr_client:
                wanted_data = sync_engine.path_mapper.bazarr_client.get_all_wanted_items()
                
                if wanted_data['total'] == 0:
                    print("🎉 No items need subtitles - everything is up to date!")
                    return
                
                print(f"📊 Found {wanted_data['total']} items needing subtitles:")
                print(f"   Movies: {len(wanted_data['movies'])}")
                print(f"   TV Episodes: {len(wanted_data['series'])}")
                print()
                
                # Show sample items
                if wanted_data['movies']:
                    print("📽️ Sample movies needing subtitles:")
                    for i, movie in enumerate(wanted_data['movies'][:3]):
                        print(f"   {i+1}. {movie.get('title', 'Unknown Title')}")
                    if len(wanted_data['movies']) > 3:
                        print(f"   ... and {len(wanted_data['movies']) - 3} more")
                
                if wanted_data['series']:
                    print("\n📺 Sample TV episodes needing subtitles:")
                    for i, episode in enumerate(wanted_data['series'][:3]):
                        series_title = episode.get('seriesTitle', 'Unknown Series')
                        episode_title = episode.get('episodeTitle', 'Unknown Episode')
                        episode_number = episode.get('episode_number', '?x?')
                        print(f"   {i+1}. {series_title} {episode_number} - {episode_title}")
                    if len(wanted_data['series']) > 3:
                        print(f"   ... and {len(wanted_data['series']) - 3} more")
                
                print("\nProcessing options:")
                print("1. Process ALL wanted items (auto-translate)")
                print("2. Process movies only")
                print("3. Process TV episodes only")
                print("4. Preview wanted items (no processing)")
                print("5. Back to main menu")
                
                try:
                    choice = input("\nChoice (1-5): ").strip()
                except EOFError:
                    print("\n👋 Input stream ended")
                    return
                
                if choice == "1":
                    self._process_all_wanted_items()
                elif choice == "2":
                    self._process_wanted_movies_only(wanted_data['movies'])
                elif choice == "3":
                    self._process_wanted_series_only(wanted_data['series'])
                elif choice == "4":
                    self._preview_wanted_items(wanted_data)
                elif choice == "5":
                    return
                else:
                    print("❌ Invalid choice")
            else:
                print("❌ Bazarr integration not available")
                
        except Exception as e:
            print(f"❌ Error accessing wanted items: {e}")
    
    def _process_all_wanted_items(self):
        """
        Process all wanted items (movies + TV episodes) with automatic translation
        
        Executes the complete wanted items workflow:
        1. Confirms user intent before processing
        2. Calls sync_engine.process_wanted_items_with_translation()
        3. Displays comprehensive results including translation counts
        4. Provides success feedback for newly created subtitle files
        """
        """Process all wanted items with translation"""
        print(f"\n🎯 PROCESSING ALL WANTED ITEMS")
        print("=" * 50)
        print("This will attempt to generate Dutch subtitles for all items")
        print("that Bazarr has marked as 'wanted' (missing subtitles).")
        print()
        
        if input("Continue with processing? (y/N): ").lower() != 'y':
            return
        
        results = sync_engine.process_wanted_items_with_translation()
        self._show_sync_results(results)
        
        if results.get('translated', 0) > 0:
            print(f"\n🎉 Successfully created {results['translated']} Dutch subtitle files!")
            print("   These subtitles were generated by translating existing English/other language subtitles.")
    
    def _process_wanted_movies_only(self, movies: list):
        """Process wanted movies only"""
        if not movies:
            print("❌ No movies need subtitles")
            return
        
        print(f"\n🎬 PROCESSING {len(movies)} WANTED MOVIES")
        print("=" * 50)
        
        if input("Continue? (y/N): ").lower() != 'y':
            return
        
        # This would need to be implemented in sync_engine if we want movie-only processing
        print("⚠️ Movie-only processing not yet implemented")
        print("   Use 'Process ALL wanted items' for now")
    
    def _process_wanted_series_only(self, series: list):
        """Process wanted TV episodes only"""
        if not series:
            print("❌ No TV episodes need subtitles")
            return
        
        print(f"\n📺 PROCESSING {len(series)} WANTED TV EPISODES")
        print("=" * 50)
        
        if input("Continue? (y/N): ").lower() != 'y':
            return
        
        # This would need to be implemented in sync_engine if we want series-only processing
        print("⚠️ TV-only processing not yet implemented")
        print("   Use 'Process ALL wanted items' for now")
    
    def _preview_wanted_items(self, wanted_data: dict):
        """
        Preview all wanted items without processing
        
        Displays a comprehensive list of items needing subtitles for user review.
        Shows up to 10 movies and 10 TV episodes with formatted titles and
        episode information. Useful for understanding scope before processing.
        
        Args:
            wanted_data (dict): Wanted items data from Bazarr containing
                              'movies' and 'series' lists
        """
        print(f"\n👀 PREVIEW: WANTED ITEMS")
        print("=" * 50)
        
        if wanted_data['movies']:
            print(f"\n🎬 Movies needing subtitles ({len(wanted_data['movies'])}):")
            for i, movie in enumerate(wanted_data['movies'][:10]):
                title = movie.get('title', 'Unknown Title')
                year = movie.get('year', 'Unknown')
                print(f"   {i+1:2d}. {title} ({year})")
            if len(wanted_data['movies']) > 10:
                print(f"   ... and {len(wanted_data['movies']) - 10} more movies")
        
        if wanted_data['series']:
            print(f"\n📺 TV Episodes needing subtitles ({len(wanted_data['series'])}):")
            for i, episode in enumerate(wanted_data['series'][:10]):
                series_title = episode.get('seriesTitle', 'Unknown Series')
                episode_title = episode.get('episodeTitle', 'Unknown Episode')
                episode_number = episode.get('episode_number', '?x?')
                # Parse season and episode from episode_number (format like "1x49")
                season_ep = episode_number.replace('x', 'E')
                if 'x' in episode_number:
                    season_ep = f"S{episode_number.replace('x', 'E')}"
                print(f"   {i+1:2d}. {series_title} {season_ep} - {episode_title}")
            if len(wanted_data['series']) > 10:
                print(f"   ... and {len(wanted_data['series']) - 10} more episodes")
        
        input("\nPress Enter to continue...")

    # =============================================================================
    # SYNC IMPLEMENTATIONS
    # =============================================================================
    
    def _sync_all_movies(self, movies: List[Dict]):
        """Sync all movies"""
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        print(f"\n🎬 SYNCING ALL {len(movies)} MOVIES")
        print("=" * 60)
        
        if input("Continue? (y/N): ").lower() != 'y':
            return
        
        results = sync_engine.batch_sync_movies(movies, language)
        self._show_sync_results(results)
    
    def _sync_all_series(self, series: List[Dict]):
        """Sync all TV series"""
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        print(f"\n📺 SYNCING ALL {len(series)} TV SERIES")
        print("=" * 60)
        
        if input("Continue? (y/N): ").lower() != 'y':
            return
        
        results = sync_engine.batch_sync_series(series, language)
        self._show_sync_results(results)
    
    def _bulk_sync_all(self):
        """Bulk sync all media"""
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        results = sync_engine.batch_sync_all(language)
        self._show_sync_results(results)
    
    def _bulk_sync_movies_only(self, movies: List[Dict]):
        """Bulk sync movies only"""
        if not movies:
            print("❌ No movies available")
            return
        
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        results = sync_engine.batch_sync_movies(movies, language)
        self._show_sync_results(results)
    
    def _bulk_sync_series_only(self, series: List[Dict]):
        """Bulk sync series only"""
        if not series:
            print("❌ No series available")
            return
        
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        results = sync_engine.batch_sync_series(series, language)
        self._show_sync_results(results)
    
    def _parallel_sync_menu(self, items: List[Dict]):
        """Parallel sync menu"""
        print(f"\n⚡ PARALLEL SYNC SETUP")
        print("=" * 40)
        print(f"Items to sync: {len(items)}")
        
        max_workers = config.get("max_workers", 2)
        print(f"Current max workers: {max_workers}")
        
        new_workers = input(f"Enter number of workers [{max_workers}]: ").strip()
        if new_workers.isdigit():
            max_workers = int(new_workers)
            if max_workers > 4:
                print("⚠️ Warning: More than 4 workers may overload your system")
                if input("Continue? (y/N): ").lower() != 'y':
                    return
        
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        print(f"\n⚡ STARTING PARALLEL SYNC")
        print(f"Workers: {max_workers}")
        print(f"Items: {len(items)}")
        print(f"Language: {language}")
        
        if input("Start parallel sync? (y/N): ").lower() == 'y':
            results = sync_engine.parallel_sync(items, language, max_workers)
            self._show_sync_results(results)
    
    def _browse_movies(self, movies: List[Dict]):
        """Browse and select movies"""
        page_size = 20
        page = 0
        
        while True:
            start = page * page_size
            end = min(start + page_size, len(movies))
            page_movies = movies[start:end]
            
            print(f"\n🎬 MOVIES ({start+1}-{end} of {len(movies)})")
            print("=" * 60)
            
            for i, movie in enumerate(page_movies, start + 1):
                title = movie.get('title', 'Unknown')
                year = movie.get('year', '????')
                print(f"{i:3d}. {title} ({year})")
            
            print(f"\nOptions:")
            print(f"Enter number (1-{end}) to sync movie")
            if end < len(movies):
                print("n - Next page")
            if page > 0:
                print("p - Previous page")
            print("b - Back to menu")
            
            choice = input("Choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == 'n' and end < len(movies):
                page += 1
            elif choice == 'p' and page > 0:
                page -= 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(movies):
                    self._sync_single_movie(movies[idx])
                else:
                    print("❌ Invalid movie number")
            else:
                print("❌ Invalid choice")
    
    def _browse_series(self, series: List[Dict]):
        """Browse and select TV series"""
        page_size = 20
        page = 0
        
        while True:
            start = page * page_size
            end = min(start + page_size, len(series))
            page_series = series[start:end]
            
            print(f"\n📺 TV SERIES ({start+1}-{end} of {len(series)})")
            print("=" * 60)
            
            for i, series_item in enumerate(page_series, start + 1):
                title = series_item.get('title', 'Unknown')
                print(f"{i:3d}. {title}")
            
            print(f"\nOptions:")
            print(f"Enter number (1-{end}) to sync series")
            if end < len(series):
                print("n - Next page")
            if page > 0:
                print("p - Previous page")
            print("b - Back to menu")
            
            choice = input("Choice: ").strip().lower()
            
            if choice == 'b':
                break
            elif choice == 'n' and end < len(series):
                page += 1
            elif choice == 'p' and page > 0:
                page -= 1
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(series):
                    self._sync_single_series(series[idx])
                else:
                    print("❌ Invalid series number")
            else:
                print("❌ Invalid choice")
    
    def _search_movies(self, movies: List[Dict]):
        """Search for specific movie"""
        query = input("Enter movie title to search: ").strip()
        if not query:
            return
        
        matches = bazarr.search_movies(query)
        
        if not matches:
            print(f"❌ No movies found matching '{query}'")
            return
        
        print(f"\n🔍 SEARCH RESULTS FOR '{query}'")
        print("=" * 60)
        
        for i, movie in enumerate(matches, 1):
            title = movie.get('title', 'Unknown')
            year = movie.get('year', '????')
            print(f"{i}. {title} ({year})")
        
        choice = input(f"\nSelect movie (1-{len(matches)}) or Enter to cancel: ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                self._sync_single_movie(matches[idx])
    
    def _search_series(self, series: List[Dict]):
        """Search for specific TV series"""
        query = input("Enter series title to search: ").strip()
        if not query:
            return
        
        matches = bazarr.search_series(query)
        
        if not matches:
            print(f"❌ No series found matching '{query}'")
            return
        
        print(f"\n🔍 SEARCH RESULTS FOR '{query}'")
        print("=" * 60)
        
        for i, series_item in enumerate(matches, 1):
            title = series_item.get('title', 'Unknown')
            print(f"{i}. {title}")
        
        choice = input(f"\nSelect series (1-{len(matches)}) or Enter to cancel: ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                self._sync_single_series(matches[idx])
    
    def _sync_single_movie(self, movie: Dict):
        """Sync a single movie"""
        title = movie.get('title', 'Unknown')
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        print(f"\n🎬 SYNCING: {title}")
        print("=" * 60)
        
        if input("Continue? (y/N): ").lower() == 'y':
            result = sync_engine.sync_bazarr_movie(movie, language)
            if result.success:
                print(f"✅ {result.message}")
            else:
                print(f"❌ {result.message}")
    
    def _sync_single_series(self, series: Dict):
        """Sync a single TV series"""
        title = series.get('title', 'Unknown')
        language = self._get_language_choice(auto_use_preferred=True)
        if not language:
            return
        
        print(f"\n📺 SYNCING: {title}")
        print("=" * 60)
        
        if input("Continue? (y/N): ").lower() == 'y':
            result = sync_engine.sync_bazarr_series(series, language)
            if result.success:
                print(f"✅ {result.message}")
            else:
                print(f"❌ {result.message}")
    
    def _quick_sync_movies(self, movies: List[Dict]):
        """Quick sync movies with Dutch subtitles"""
        print("\n🚀 QUICK SYNC - MOVIES WITH DUTCH SUBTITLES")
        print("=" * 60)
        
        # Find movies with Dutch subtitles
        dutch_movies = []
        for movie in movies:
            subtitles = movie.get('subtitles', [])
            if any(s.get('language') == 'nl' for s in subtitles):
                dutch_movies.append(movie)
        
        if not dutch_movies:
            print("❌ No movies found with Dutch subtitles")
            return
        
        print(f"Found {len(dutch_movies)} movies with Dutch subtitles")
        
        if input("Quick sync these movies? (y/N): ").lower() == 'y':
            results = sync_engine.batch_sync_movies(dutch_movies, "nl")
            self._show_sync_results(results)
    
    def _quick_sync_series(self, series: List[Dict]):
        """Quick sync series with Dutch subtitles"""
        print("\n🚀 QUICK SYNC - SERIES WITH DUTCH SUBTITLES")
        print("=" * 60)
        
        # Find series with Dutch subtitles
        dutch_series = []
        for series_item in series:
            episodes = series_item.get('episodes', [])
            has_dutch = any(
                any(s.get('language') == 'nl' for s in ep.get('subtitles', []))
                for ep in episodes
            )
            if has_dutch:
                dutch_series.append(series_item)
        
        if not dutch_series:
            print("❌ No series found with Dutch subtitles")
            return
        
        print(f"Found {len(dutch_series)} series with Dutch subtitles")
        
        if input("Quick sync these series? (y/N): ").lower() == 'y':
            results = sync_engine.batch_sync_series(dutch_series, "nl")
            self._show_sync_results(results)
    
    # =============================================================================
    # STATISTICS MENU
    # =============================================================================
    
    def _statistics_menu(self):
        """Statistics and reports menu"""
        print("\n📊 STATISTICS & REPORTS")
        print("=" * 50)
        print("1. Show sync statistics (7 days)")
        print("2. Show sync statistics (30 days)")
        print("3. Show recent sync activity")
        print("4. Show failed syncs")
        print("5. Export full report")
        print("6. Database health check")
        print("7. Back to main menu")
        
        choice = input("\nChoice (1-7): ").strip()
        
        if choice == "1":
            sync_engine.show_sync_statistics(7)
        elif choice == "2":
            sync_engine.show_sync_statistics(30)
        elif choice == "3":
            self._show_recent_activity()
        elif choice == "4":
            self._show_failed_syncs()
        elif choice == "5":
            self._export_report()
        elif choice == "6":
            self._database_health_check()
        elif choice == "7":
            return
        else:
            print("❌ Invalid choice")
    
    def _show_recent_activity(self):
        """Show recent sync activity"""
        print("\n📋 RECENT SYNC ACTIVITY")
        print("=" * 60)
        
        recent = database.get_recent_syncs(20)
        
        if not recent:
            print("📭 No recent activity")
            return
        
        for activity in recent:
            video_path, subtitle_path, language, status, sync_time, date = activity
            video_name = os.path.basename(video_path)
            status_icon = "✅" if status == "success" else "❌"
            
            print(f"{status_icon} {video_name} ({language}) - {date}")
            if sync_time:
                print(f"    Time: {sync_time:.1f}s")
    
    def _show_failed_syncs(self):
        """Show failed syncs for troubleshooting"""
        print("\n❌ FAILED SYNCS (Last 7 days)")
        print("=" * 60)
        
        failed = database.get_failed_syncs(7)
        
        if not failed:
            print("✅ No failed syncs found!")
            return
        
        for fail in failed:
            video_path, subtitle_path, language, method, date = fail
            video_name = os.path.basename(video_path)
            print(f"❌ {video_name} ({language}) - {date}")
            print(f"    Method: {method}")
    
    def _export_report(self):
        """Export comprehensive report"""
        filename = input("Report filename [auto]: ").strip()
        
        if database.export_report(filename if filename else None):
            print("✅ Report exported successfully!")
        else:
            print("❌ Failed to export report")
    
    def _database_health_check(self):
        """Show database health"""
        print("\n🏥 DATABASE HEALTH CHECK")
        print("=" * 50)
        
        health = database.health_check()
        
        for key, value in health.items():
            if key == "error":
                print(f"❌ Error: {value}")
            elif isinstance(value, bool):
                icon = "✅" if value else "❌"
                print(f"{icon} {key.replace('_', ' ').title()}: {value}")
            else:
                print(f"📊 {key.replace('_', ' ').title()}: {value}")
    
    # =============================================================================
    # SETTINGS MENU
    # =============================================================================
    
    def _settings_menu(self):
        """Settings and configuration menu"""
        print("\n⚙️ SETTINGS & CONFIGURATION")
        print("=" * 50)
        print("1. Configure Bazarr credentials")
        print("2. Test Bazarr connection")
        print("3. Configure Plex credentials")
        print("4. Test Plex connection")
        print("5. Configure path mappings")
        print("6. Set preferred languages")
        print("7. Configure sync settings")
        print("8. Show current configuration")
        print("9. Reset to defaults")
        print("10. Back to main menu")
        
        choice = input("\nChoice (1-10): ").strip()
        
        if choice == "1":
            bazarr.configure_credentials()
        elif choice == "2":
            if bazarr.test_connection():
                print("✅ Bazarr connection successful!")
            else:
                print("❌ Bazarr connection failed")
        elif choice == "3":
            self._configure_plex_credentials()
        elif choice == "4":
            self._test_plex_connection()
        elif choice == "5":
            self._configure_path_mappings()
        elif choice == "6":
            self._configure_languages()
        elif choice == "7":
            self._configure_sync_settings()
        elif choice == "8":
            config.show_current_config()
        elif choice == "9":
            if input("Reset all settings to defaults? (y/N): ").lower() == 'y':
                config.reset_to_defaults()
                print("✅ Settings reset to defaults")
        elif choice == "10":
            return
        else:
            print("❌ Invalid choice")
    
    def _configure_languages(self):
        """Configure preferred languages"""
        current = config.get("preferred_languages", ["nl", "en"])
        print(f"\nCurrent languages: {', '.join(current)}")
        
        new_langs = input("Enter languages (comma-separated): ").strip()
        if new_langs:
            languages = [lang.strip() for lang in new_langs.split(",")]
            config.set("preferred_languages", languages)
            print(f"✅ Languages updated: {', '.join(languages)}")
    
    def _configure_sync_settings(self):
        """Configure sync settings"""
        print("\n⚙️ SYNC SETTINGS")
        print("=" * 30)
        
        settings = [
            ("max_workers", "Max workers", int),
            ("sync_timeout", "Sync timeout (seconds)", int),
            ("vad_method", "VAD method", str),
            ("auto_archive", "Auto archive", bool),
            ("plex_integration", "Plex integration", bool)
        ]
        
        for key, label, type_func in settings:
            current = config.get(key)
            if type_func == bool:
                new_value = input(f"{label} [{'yes' if current else 'no'}]: ").strip().lower()
                if new_value in ['y', 'yes', 'true', '1']:
                    config.set(key, True)
                elif new_value in ['n', 'no', 'false', '0']:
                    config.set(key, False)
            else:
                new_value = input(f"{label} [{current}]: ").strip()
                if new_value:
                    try:
                        config.set(key, type_func(new_value))
                    except ValueError:
                        print(f"❌ Invalid value for {label}")
    
    def _configure_plex_credentials(self):
        """Configure Plex server credentials"""
        print("\n🎬 PLEX CONFIGURATION")
        print("=" * 50)
        
        # Get Plex URL
        current_url = config.get("plex_url", "http://192.168.90.3:32400")
        print(f"Current Plex URL: {current_url}")
        new_url = input("Enter Plex server URL (or press Enter to keep current): ").strip()
        if new_url:
            config.set("plex_url", new_url)
            print(f"✅ Plex URL updated to: {new_url}")
        
        # Get Plex Token
        current_token = config.get("plex_token")
        if current_token:
            print("✅ Plex token is already configured")
            if input("Update Plex token? (y/N): ").lower() == 'y':
                self._get_plex_token()
        else:
            print("❌ No Plex token configured")
            if input("Get Plex token now? (Y/n): ").lower() != 'n':
                self._get_plex_token()
    
    def _get_plex_token(self):
        """Get Plex authentication token"""
        print("\n🔑 PLEX TOKEN RETRIEVAL")
        print("=" * 40)
        print("Choose token retrieval method:")
        print("1. Enter token manually")
        print("2. Get token using username/password")
        print("3. Cancel")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == "1":
            token = input("Enter your Plex token: ").strip()
            if token:
                config.set("plex_token", token)
                print("✅ Plex token saved")
            else:
                print("❌ No token entered")
        
        elif choice == "2":
            # Import and use the get_plex_token module
            try:
                from get_plex_token import get_plex_token
                token = get_plex_token()
                if token:
                    config.set("plex_token", token)
                    print("✅ Plex token saved")
                else:
                    print("❌ Failed to get token")
            except ImportError:
                print("❌ get_plex_token module not found")
            except Exception as e:
                print(f"❌ Error getting token: {e}")
        
        elif choice == "3":
            print("Token retrieval cancelled")
        else:
            print("❌ Invalid choice")
    
    def _test_plex_connection(self):
        """Test Plex server connection"""
        plex_url = config.get("plex_url")
        plex_token = config.get("plex_token")
        
        if not plex_url or not plex_token:
            print("❌ Plex credentials not configured")
            print("💡 Use 'Configure Plex credentials' first")
            return
        
        try:
            from plex_client import PlexSubtitleManager
            plex_client = PlexSubtitleManager(plex_url, plex_token)
            
            if plex_client.test_connection():
                print("✅ Plex connection successful!")
                
                # Show libraries
                libraries = plex_client.get_libraries()
                if libraries:
                    print(f"\n📚 Found {len(libraries)} libraries:")
                    for lib in libraries:
                        print(f"   • {lib['title']} ({lib['type']})")
            else:
                print("❌ Plex connection failed")
                
        except ImportError:
            print("❌ plex_client module not found")
        except Exception as e:
            print(f"❌ Error testing Plex connection: {e}")

    def _configure_path_mappings(self):
        """Configure path mappings for different environments"""
        print("\n🗺️ PATH MAPPING CONFIGURATION")
        print("=" * 50)
        
        # Show current environment
        current_env = config.get("current_environment", "mac_local")
        env_paths = config.get("environment_paths", {})
        
        if current_env in env_paths:
            current_desc = env_paths[current_env].get("description", "Unknown")
            print(f"📍 Current Environment: {current_env} ({current_desc})")
        else:
            print(f"📍 Current Environment: {current_env} (Custom)")
        
        print("\n🔧 Path Management Options:")
        print("1. Switch environment profile")
        print("2. View current path mappings")
        print("3. Edit current environment paths")
        print("4. Create new environment profile")
        print("5. Delete environment profile")
        print("6. Test path accessibility")
        print("7. Back to settings menu")
        
        choice = input("\nChoice (1-7): ").strip()
        
        if choice == "1":
            self._switch_environment()
        elif choice == "2":
            self._view_path_mappings()
        elif choice == "3":
            self._edit_environment_paths()
        elif choice == "4":
            self._create_environment_profile()
        elif choice == "5":
            self._delete_environment_profile()
        elif choice == "6":
            self._test_path_accessibility()
        elif choice == "7":
            return
        else:
            print("❌ Invalid choice")
    
    def _switch_environment(self):
        """Switch to a different environment profile"""
        env_paths = config.get("environment_paths", {})
        current_env = config.get("current_environment", "mac_local")
        
        if not env_paths:
            print("❌ No environment profiles configured")
            return
        
        print("\n🌍 AVAILABLE ENVIRONMENTS:")
        print("=" * 40)
        
        for i, (env_key, env_data) in enumerate(env_paths.items(), 1):
            current_marker = "🟢" if env_key == current_env else "⭕"
            description = env_data.get("description", "No description")
            print(f"{i}. {current_marker} {env_key}: {description}")
        
        print(f"{len(env_paths) + 1}. Cancel")
        
        try:
            choice = int(input(f"\nSelect environment (1-{len(env_paths) + 1}): "))
            if choice == len(env_paths) + 1:
                return
            
            env_keys = list(env_paths.keys())
            if 1 <= choice <= len(env_keys):
                selected_env = env_keys[choice - 1]
                config.set("current_environment", selected_env)
                print(f"✅ Switched to environment: {selected_env}")
                
                # Update path mappings based on new environment
                self._update_path_mappings_from_environment()
            else:
                print("❌ Invalid selection")
                
        except ValueError:
            print("❌ Invalid input")
    
    def _view_path_mappings(self):
        """View current path mappings"""
        current_env = config.get("current_environment", "mac_local")
        env_paths = config.get("environment_paths", {})
        
        print(f"\n🗺️ CURRENT PATH MAPPINGS ({current_env})")
        print("=" * 50)
        
        if current_env in env_paths:
            env_data = env_paths[current_env]
            print(f"📝 Description: {env_data.get('description', 'No description')}")
            print()
            print("🎬 MOVIES:")
            print(f"   Local:  {env_data.get('movies_local', 'Not configured')}")
            print(f"   Plex:   {env_data.get('movies_plex', 'Not configured')}")
            print()
            print("📺 TV SERIES:")
            print(f"   Local:  {env_data.get('series_local', 'Not configured')}")
            print(f"   Plex:   {env_data.get('series_plex', 'Not configured')}")
        else:
            print("❌ Current environment not found in configuration")
            
        print(f"\n🔄 Legacy path_mappings:")
        path_mappings = config.get("path_mappings", {})
        for plex_path, local_path in path_mappings.items():
            print(f"   {plex_path} → {local_path}")
    
    def _edit_environment_paths(self):
        """Edit paths for current environment"""
        current_env = config.get("current_environment", "mac_local")
        env_paths = config.get("environment_paths", {})
        
        if current_env not in env_paths:
            print(f"❌ Environment '{current_env}' not found")
            return
        
        env_data = env_paths[current_env].copy()
        
        print(f"\n✏️ EDITING ENVIRONMENT: {current_env}")
        print("=" * 50)
        print("Press Enter to keep current value")
        print()
        
        # Edit each path
        fields = [
            ("description", "Description"),
            ("movies_local", "Movies Local Path"),
            ("movies_plex", "Movies Plex Path"),
            ("series_local", "TV Series Local Path"),
            ("series_plex", "TV Series Plex Path")
        ]
        
        for field_key, field_label in fields:
            current_value = env_data.get(field_key, "")
            new_value = input(f"{field_label} [{current_value}]: ").strip()
            if new_value:
                env_data[field_key] = new_value
        
        # Save changes
        env_paths[current_env] = env_data
        config.set("environment_paths", env_paths)
        
        print("✅ Environment paths updated")
        
        # Update path mappings
        self._update_path_mappings_from_environment()
    
    def _create_environment_profile(self):
        """Create a new environment profile"""
        print("\n🆕 CREATE NEW ENVIRONMENT")
        print("=" * 40)
        
        env_key = input("Environment key (e.g., 'my_setup'): ").strip()
        if not env_key:
            print("❌ Environment key required")
            return
        
        env_paths = config.get("environment_paths", {})
        if env_key in env_paths:
            print(f"❌ Environment '{env_key}' already exists")
            return
        
        # Get environment details
        description = input("Description: ").strip()
        movies_local = input("Movies local path: ").strip()
        movies_plex = input("Movies Plex path: ").strip()
        series_local = input("TV Series local path: ").strip()
        series_plex = input("TV Series Plex path: ").strip()
        
        # Create new environment
        new_env = {
            "description": description or f"Custom environment: {env_key}",
            "movies_local": movies_local,
            "movies_plex": movies_plex,
            "series_local": series_local,
            "series_plex": series_plex
        }
        
        env_paths[env_key] = new_env
        config.set("environment_paths", env_paths)
        
        print(f"✅ Environment '{env_key}' created")
        
        # Ask if user wants to switch to it
        if input("Switch to this environment now? (y/N): ").lower() == 'y':
            config.set("current_environment", env_key)
            self._update_path_mappings_from_environment()
            print(f"✅ Switched to environment: {env_key}")
    
    def _delete_environment_profile(self):
        """Delete an environment profile"""
        env_paths = config.get("environment_paths", {})
        current_env = config.get("current_environment", "mac_local")
        
        if not env_paths:
            print("❌ No environment profiles to delete")
            return
        
        print("\n🗑️ DELETE ENVIRONMENT")
        print("=" * 30)
        
        for i, (env_key, env_data) in enumerate(env_paths.items(), 1):
            current_marker = "🟢" if env_key == current_env else "⭕"
            description = env_data.get("description", "No description")
            print(f"{i}. {current_marker} {env_key}: {description}")
        
        print(f"{len(env_paths) + 1}. Cancel")
        
        try:
            choice = int(input(f"\nSelect environment to delete (1-{len(env_paths) + 1}): "))
            if choice == len(env_paths) + 1:
                return
            
            env_keys = list(env_paths.keys())
            if 1 <= choice <= len(env_keys):
                selected_env = env_keys[choice - 1]
                
                if selected_env == current_env:
                    print("❌ Cannot delete current active environment")
                    print("💡 Switch to another environment first")
                    return
                
                if input(f"Delete environment '{selected_env}'? (y/N): ").lower() == 'y':
                    del env_paths[selected_env]
                    config.set("environment_paths", env_paths)
                    print(f"✅ Environment '{selected_env}' deleted")
            else:
                print("❌ Invalid selection")
                
        except ValueError:
            print("❌ Invalid input")
    
    def _test_path_accessibility(self):
        """Test if configured paths are accessible"""
        current_env = config.get("current_environment", "mac_local")
        env_paths = config.get("environment_paths", {})
        
        if current_env not in env_paths:
            print("❌ Current environment not configured")
            return
        
        env_data = env_paths[current_env]
        
        print(f"\n🧪 TESTING PATH ACCESSIBILITY ({current_env})")
        print("=" * 50)
        
        paths_to_test = [
            ("Movies Local", env_data.get("movies_local")),
            ("Series Local", env_data.get("series_local"))
        ]
        
        for label, path in paths_to_test:
            if not path:
                print(f"⚠️ {label}: Not configured")
                continue
            
            try:
                import os
                if os.path.exists(path):
                    print(f"✅ {label}: {path}")
                else:
                    print(f"❌ {label}: {path} (Not accessible)")
            except Exception as e:
                print(f"❌ {label}: {path} (Error: {e})")
    
    def _update_path_mappings_from_environment(self):
        """Update legacy path_mappings from current environment"""
        current_env = config.get("current_environment", "mac_local")
        env_paths = config.get("environment_paths", {})
        
        if current_env not in env_paths:
            return
        
        env_data = env_paths[current_env]
        
        # Update path mappings
        new_mappings = {}
        
        if env_data.get("movies_plex") and env_data.get("movies_local"):
            new_mappings[env_data["movies_plex"]] = env_data["movies_local"]
        
        if env_data.get("series_plex") and env_data.get("series_local"):
            new_mappings[env_data["series_plex"]] = env_data["series_local"]
        
        config.set("path_mappings", new_mappings)
        print("🔄 Path mappings updated from environment")

    # =============================================================================
    # ARCHIVE MENU
    # =============================================================================
    
    def _archive_menu(self):
        """Archive management menu"""
        print("\n📦 ARCHIVE MANAGEMENT")
        print("=" * 50)
        
        if not sync_engine.archive_manager:
            print("❌ Archive manager not available")
            print("💡 Enable auto_archive in settings to use archive features")
            return
        
        print("1. Show archive statistics")
        print("2. View archived files")
        print("3. Restore files")
        print("4. Clean old archives")
        print("5. Back to main menu")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            self._show_archive_stats()
        elif choice == "2":
            self._view_archived_files()
        elif choice == "3":
            self._restore_files_menu()
        elif choice == "4":
            self._clean_archives()
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")
    
    def _show_archive_stats(self):
        """Show archive statistics"""
        if sync_engine.archive_manager:
            stats = sync_engine.archive_manager.get_archive_statistics()
            if stats:
                print("\n📊 ARCHIVE STATISTICS")
                print("=" * 40)
                print(f"Total files: {stats['total_files']}")
                print(f"Original files: {stats['original_files']}")
                print(f"Backup files: {stats['backup_files']}")
                print(f"Total size: {stats['total_size_mb']:.1f} MB")
                if stats['first_archive']:
                    print(f"First archive: {stats['first_archive']}")
                if stats['last_archive']:
                    print(f"Last archive: {stats['last_archive']}")
            else:
                print("📭 No archive statistics available")
    
    def _view_archived_files(self):
        """View archived files"""
        print("📦 Archive file viewing not yet implemented")
        print("💡 Use the archive manager's show_restore_menu() method")
    
    def _restore_files_menu(self):
        """Restore files menu"""
        if sync_engine.archive_manager:
            sync_engine.archive_manager.show_restore_menu()
        else:
            print("❌ Archive manager not available")
    
    def _clean_archives(self):
        """Clean old archives"""
        print("🧹 Archive cleanup not yet implemented")
        print("💡 This feature will clean archives older than 30 days")
    
    # =============================================================================
    # TOOLS MENU
    # =============================================================================
    
    def _tools_menu(self):
        """System tools menu"""
        print("\n🔧 SYSTEM TOOLS")
        print("=" * 40)
        print("1. Flush credentials")
        print("2. Flush sync history")
        print("3. Clear Bazarr cache")
        print("4. System health check")
        print("5. Debug information")
        print("6. 🔐 Fix archive permissions")
        print("7. Back to main menu")
        
        choice = input("\nChoice (1-7): ").strip()
        
        if choice == "1":
            if input("Delete all saved credentials? (y/N): ").lower() == 'y':
                if database.flush_credentials():
                    print("✅ Credentials flushed")
                else:
                    print("❌ Failed to flush credentials")
        elif choice == "2":
            if input("Delete all sync history? (y/N): ").lower() == 'y':
                if database.flush_sync_history():
                    print("✅ Sync history flushed")
                else:
                    print("❌ Failed to flush sync history")
        elif choice == "3":
            bazarr.clear_cache()
        elif choice == "4":
            self._system_health_check()
        elif choice == "5":
            self._debug_info()
        elif choice == "6":
            self._fix_archive_permissions()
        elif choice == "7":
            return
        else:
            print("❌ Invalid choice")
    
    def _system_health_check(self):
        """Comprehensive system health check"""
        print("\n🏥 SYSTEM HEALTH CHECK")
        print("=" * 50)
        
        # Check sync engine
        sync_health = sync_engine.health_check()
        print("🔧 Sync Engine:")
        for key, value in sync_health.items():
            icon = "✅" if value else "❌"
            print(f"  {icon} {key.replace('_', ' ').title()}")
        
        # Check database
        db_health = database.health_check()
        print("\n💾 Database:")
        for key, value in db_health.items():
            if key != "error":
                icon = "✅" if value else "❌"
                print(f"  {icon} {key.replace('_', ' ').title()}")
        
        # Check Bazarr
        print("\n🌐 Bazarr:")
        print(f"  {'✅' if bazarr.is_configured() else '❌'} Configured")
        print(f"  {'✅' if bazarr.test_connection() else '❌'} Connected")
        
        # Check configuration
        print("\n⚙️ Configuration:")
        print(f"  ✅ Config loaded")
        print(f"  ✅ Settings available")
    
    def _debug_info(self):
        """Show debug information"""
        print("\n🐛 DEBUG INFORMATION")
        print("=" * 50)
        
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Database path: {database.db_path}")
        print(f"Config file: {config.config_file}")
        
        # Module availability
        print(f"\nModule availability:")
        print(f"  PathMapper: {'✅' if sync_engine.use_pathmapper else '❌'}")
        print(f"  Archive Manager: {'✅' if sync_engine.archive_manager else '❌'}")
        print(f"  Core Database: {'✅' if database.use_core else '❌'}")
        print(f"  Core Bazarr: {'✅' if bazarr.use_core else '❌'}")
        
        # Media stats
        if bazarr.cache_valid:
            stats = bazarr.get_media_stats()
            print(f"\nBazarr media cache:")
            print(f"  Movies: {stats['total_movies']}")
            print(f"  Series: {stats['total_series']}")
            print(f"  Languages: {len(stats['languages'])}")
    
    # =============================================================================
    # HELP MENU
    # =============================================================================
    
    def _help_menu(self):
        """Help and status menu"""
        print("\n❓ HELP & STATUS")
        print("=" * 40)
        print("1. Show system status")
        print("2. Show Bazarr status")
        print("3. Show configuration")
        print("4. About this system")
        print("5. Back to main menu")
        
        choice = input("\nChoice (1-5): ").strip()
        
        if choice == "1":
            self._show_system_status()
        elif choice == "2":
            bazarr.show_status()
        elif choice == "3":
            config.show_current_config()
        elif choice == "4":
            self._show_about()
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice")
    
    def _show_system_status(self):
        """Show overall system status"""
        print("\n📊 SYSTEM STATUS")
        print("=" * 50)
        
        print("🔧 Core Components:")
        print(f"  Sync Engine: {'✅ PathMapper' if sync_engine.use_pathmapper else '⚠️ Fallback'}")
        print(f"  Database: {'✅ Core' if database.use_core else '⚠️ Fallback'}")
        print(f"  Bazarr: {'✅ Core' if bazarr.use_core else '⚠️ Fallback'}")
        print(f"  Archive: {'✅ Available' if sync_engine.archive_manager else '❌ Disabled'}")
        
        print("\n🌐 Services:")
        print(f"  Bazarr: {'✅ Connected' if bazarr.test_connection() else '❌ Disconnected'}")
        
        print("\n📊 Statistics:")
        stats = database.get_statistics(7)
        print(f"  Recent syncs (7d): {stats.get('total', 0)}")
        print(f"  Success rate: {stats.get('success_rate', 0):.1f}%")
    
    def _show_about(self):
        """Show about information"""
        print("\n🚀 ABOUT SUBTITLE SYNC SYSTEM")
        print("=" * 60)
        print("A powerful subtitle synchronization system that combines:")
        print()
        print("🔥 PathMapper Engine:")
        print("   • Advanced path mapping and file discovery")
        print("   • Smart duplicate detection")
        print("   • Multiple VAD method fallbacks")
        print("   • Comprehensive session tracking")
        print()
        print("🌐 Bazarr Integration:")
        print("   • Seamless media discovery")
        print("   • Automatic subtitle detection")
        print("   • Hybrid sync capabilities")
        print()
        print("📦 Archive Management:")
        print("   • Automatic backup before sync")
        print("   • Easy restore functionality")
        print("   • Archive statistics and cleanup")
        print()
        print("💪 Powered by your existing PathMapper module!")
    
    def _fix_archive_permissions(self):
        """Fix archive directory permissions"""
        print("\n🔐 ARCHIVE PERMISSION FIXER")
        print("=" * 50)
        
        import getpass
        archive_dir = os.path.expanduser("~/subtitle_archive")
        username = getpass.getuser()
        
        print(f"📁 Archive directory: {archive_dir}")
        print(f"👤 Current user: {username}")
        
        if not os.path.exists(archive_dir):
            print("📁 Archive directory doesn't exist yet - will be created on first run")
            input("\nPress Enter to continue...")
            return
        
        try:
            # Check current ownership
            stat_info = os.stat(archive_dir)
            current_uid = stat_info.st_uid
            current_user_uid = os.getuid()
            
            if current_uid != current_user_uid:
                print(f"❌ Archive directory owned by UID {current_uid}, but you are UID {current_user_uid}")
                print(f"\n💡 To fix this, run:")
                print(f"   sudo chown -R {username} {archive_dir}")
                print(f"\n🚨 You may need to run this command outside the script")
                input("\nPress Enter to continue...")
                return
            
            # Check if writable
            if os.access(archive_dir, os.W_OK):
                print("✅ Archive directory permissions are correct!")
                
                # Test with a small file
                try:
                    test_file = os.path.join(archive_dir, ".permission_test")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    print("✅ Write test successful!")
                except Exception as e:
                    print(f"❌ Write test failed: {e}")
                    
            else:
                print(f"❌ Archive directory is not writable")
                print(f"\n💡 To fix this, run:")
                print(f"   chmod 755 {archive_dir}")
                
        except Exception as e:
            print(f"❌ Error checking permissions: {e}")
        
        input("\nPress Enter to continue...")

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _get_language_choice(self, auto_use_preferred: bool = True) -> Optional[str]:
        """Get language choice from user or use preferred setting"""
        preferred = config.get("preferred_languages", ["nl", "en"])
        default = preferred[0] if preferred else "nl"
        
        # If auto_use_preferred is True and we have a preferred language, use it
        if auto_use_preferred and preferred:
            print(f"Using preferred language: {default}")
            return default
        
        # Otherwise prompt the user
        language = input(f"Language [{default}]: ").strip()
        return language if language else default
    
    def _show_sync_results(self, results: Dict[str, int]):
        """Show sync operation results"""
        print(f"\n🎉 SYNC RESULTS")
        print("=" * 40)
        print(f"✅ Successful: {results['successful']}")
        
        # Show translation results if available
        if 'translated' in results and results['translated'] > 0:
            print(f"🌍 Translated: {results['translated']}")
        
        print(f"⭐ Skipped: {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        
        total = sum(v for k, v in results.items() if k != 'translated')
        if total > 0:
            success_rate = (results['successful'] / total) * 100
            print(f"📊 Success rate: {success_rate:.1f}%")
    
    def _exit(self):
        """Exit the application"""
        print("\n👋 Thank you for using Subtitle Sync System!")
        print("💪 Powered by PathMapper Engine")
        self.running = False

# Global CLI instance
cli = SubtitleSyncCLI()
