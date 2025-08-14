"""
Path Mapper - Maps Bazarr server paths to local Mac paths and handles sync coordination with tracking
"""

import os
import re
import subprocess
import shutil
import time
import hashlib
import sqlite3
from pathlib import Path

def get_logger(name):
    """Simple logger fallback"""
    import logging
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

class PathMapper:
    def __init__(self, bazarr_client):
        self.bazarr_client = bazarr_client
        self.logger = get_logger('PathMapper')
        
        # Path mapping rules
        self.path_mappings = {
            # Bazarr server paths -> Local Mac paths
            "/PlexMedia/Movies": "/Volumes/Data/Movies",
            "/PlexMedia/TVShows": "/Volumes/Data/TVShows",
            "/PlexMedia/Cartoons": "/Volumes/Data/Movies",  # If you have cartoons
        }
        
        # Alternative local search paths
        self.local_search_paths = [
            "/Volumes/Data/Movies",
            "/Volumes/Data/TVShows",
            "/Volumes/Data/Christmas",
            "/Volumes/Data",
        ]
        
        # Initialize sync tracking database
        self.init_sync_database()
    
    def init_sync_database(self):
        """Initialize SQLite database for tracking sync history"""
        try:
            db_path = os.path.expanduser("~/subtitle_sync_history.db")
            self.conn = sqlite3.connect(db_path)
            
            # Create sync history table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_path TEXT NOT NULL,
                    subtitle_path TEXT NOT NULL,
                    synced_subtitle_path TEXT NOT NULL,
                    video_hash TEXT,
                    subtitle_hash TEXT,
                    sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sync_offset REAL,
                    processing_time REAL,
                    sync_method TEXT,
                    status TEXT,
                    UNIQUE(video_path, subtitle_path)
                )
            """)
            
            self.conn.commit()
            print(f"   📊 Sync tracking database initialized: {db_path}")
            
        except Exception as e:
            print(f"   ⚠️ Could not initialize sync database: {e}")
            self.conn = None
    
    def get_file_hash(self, file_path, sample_size=1024*1024):
        """Get a quick hash of file (first 1MB) for change detection"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                hasher.update(f.read(sample_size))
            return hasher.hexdigest()
        except:
            return None
    
    def is_already_synced(self, video_path, subtitle_path):
        """Check if subtitle is already synced and up to date"""
        if not self.conn:
            return False, None
        
        try:
            # First check if .synced.srt file exists
            synced_path = self.get_synced_subtitle_path(subtitle_path)
            if os.path.exists(synced_path):
                print(f"   ✅ Found existing synced subtitle: {os.path.basename(synced_path)}")
                
                # Check database for sync details
                cursor = self.conn.execute("""
                    SELECT sync_timestamp, sync_offset, processing_time, sync_method, video_hash, subtitle_hash
                    FROM sync_history 
                    WHERE video_path = ? AND subtitle_path = ?
                    ORDER BY sync_timestamp DESC LIMIT 1
                """, (video_path, subtitle_path))
                
                result = cursor.fetchone()
                if result:
                    timestamp, offset, proc_time, method, old_video_hash, old_sub_hash = result
                    
                    # Check if files have changed since last sync
                    current_video_hash = self.get_file_hash(video_path)
                    current_sub_hash = self.get_file_hash(subtitle_path)
                    
                    if (current_video_hash == old_video_hash and 
                        current_sub_hash == old_sub_hash):
                        print(f"   ✅ Subtitle already synced on {timestamp}")
                        print(f"   📊 Previous sync: offset={offset:.3f}s, time={proc_time:.1f}s, method={method}")
                        return True, synced_path
                    else:
                        print(f"   ⚠️ Files changed since last sync - will re-sync")
                else:
                    print(f"   ⚠️ Synced file exists but no database record - will verify")
                
                return True, synced_path  # Use existing synced file anyway
            
            return False, None
            
        except Exception as e:
            print(f"   ⚠️ Error checking sync status: {e}")
            return False, None
    
    def get_synced_subtitle_path(self, original_subtitle_path):
        """Get the path for the synced subtitle file"""
        base_path = os.path.splitext(original_subtitle_path)[0]
        return f"{base_path}.synced.srt"
    
    def record_sync_result(self, video_path, subtitle_path, synced_path, success, offset=0.0, processing_time=0.0, method="ffsubsync"):
        """Record sync result in database"""
        if not self.conn:
            return
        
        try:
            video_hash = self.get_file_hash(video_path)
            subtitle_hash = self.get_file_hash(subtitle_path)
            
            # Insert or replace sync record
            self.conn.execute("""
                INSERT OR REPLACE INTO sync_history 
                (video_path, subtitle_path, synced_subtitle_path, video_hash, subtitle_hash,
                 sync_offset, processing_time, sync_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_path, subtitle_path, synced_path, video_hash, subtitle_hash,
                offset, processing_time, method, "success" if success else "failed"
            ))
            
            self.conn.commit()
            print(f"   📊 Sync result recorded in database")
            
        except Exception as e:
            print(f"   ⚠️ Could not record sync result: {e}")
    
    def get_sync_statistics(self):
        """Get sync statistics from database"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_syncs,
                    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_syncs,
                    AVG(CASE WHEN status = 'success' THEN processing_time END) as avg_time,
                    MIN(sync_timestamp) as first_sync,
                    MAX(sync_timestamp) as last_sync
                FROM sync_history
            """)
            
            result = cursor.fetchone()
            if result:
                total, success, avg_time, first, last = result
                return {
                    'total_syncs': total,
                    'successful_syncs': success,
                    'success_rate': (success / total * 100) if total > 0 else 0,
                    'avg_processing_time': avg_time or 0,
                    'first_sync': first,
                    'last_sync': last
                }
        except Exception as e:
            print(f"   ⚠️ Error getting statistics: {e}")
        
        return None

    def map_bazarr_path_to_local(self, bazarr_path):
        """Map a Bazarr server path to local Mac path"""
        if not bazarr_path:
            return None
            
        # Try direct mapping first
        for server_path, local_path in self.path_mappings.items():
            if bazarr_path.startswith(server_path):
                local_mapped = bazarr_path.replace(server_path, local_path)
                if os.path.exists(local_mapped):
                    print(f"   ✅ Direct mapping found: {local_mapped}")
                    return local_mapped
        
        # Try fuzzy matching by filename
        filename = os.path.basename(bazarr_path)
        print(f"   🔍 Searching for file: {filename}")
        
        for search_path in self.local_search_paths:
            if not os.path.exists(search_path):
                continue
                
            for root, dirs, files in os.walk(search_path):
                if filename in files:
                    found_path = os.path.join(root, filename)
                    print(f"   ✅ Fuzzy match found: {found_path}")
                    return found_path
        
        print(f"   ❌ No local mapping found for: {bazarr_path}")
        return None
    
    def find_matching_subtitle(self, video_path, language="nl"):
        """Find matching subtitle file for a video - ONLY original files, not synced"""
        if not video_path or not os.path.exists(video_path):
            return None
            
        video_dir = os.path.dirname(video_path)
        video_base = os.path.splitext(os.path.basename(video_path))[0]
        
        # Look for original subtitles to sync (exclude synced files)
        original_patterns = [
            f"{video_base}.{language}.srt",
            f"{video_base}.{language}.hi.srt",
            f"{video_base}.{language}.forced.srt",
            f"{video_base}.*.{language}.srt",
            f"{video_base}.{language}.*.srt",
        ]
        
        # If Dutch, try additional patterns
        if language.lower() in ['nl', 'dutch', 'nederlands']:
            original_patterns.extend([
                f"{video_base}.dutch.srt",
                f"{video_base}.nederlands.srt",
                f"{video_base}.nld.srt",
            ])
        
        for pattern in original_patterns:
            matches = []
            try:
                import glob
                full_pattern = os.path.join(video_dir, pattern)
                matches = glob.glob(full_pattern)
            except:
                # Fallback to simple check
                simple_path = os.path.join(video_dir, pattern)
                if os.path.exists(simple_path):
                    matches = [simple_path]
            
            if matches:
                # Prefer non-HI subtitles
                for match in matches:
                    if '.hi.' not in match.lower() and '.synced.' not in match.lower():
                        print(f"   ✅ Found subtitle to sync: {os.path.basename(match)}")
                        return match
                # Use any match as fallback
                for match in matches:
                    if '.synced.' not in match.lower():
                        print(f"   ✅ Found subtitle (HI) to sync: {os.path.basename(matches[0])}")
                        return matches[0]
        
        print(f"   ❌ No subtitle found for {os.path.basename(video_path)}")
        return None
    
    def sync_using_simple_method(self, video_path, subtitle_path):
        """Use the corrected ffsubsync method with smart sync tracking"""
        print(f"   🎯 Starting Mac M1 sync process...")
        print(f"   📹 Video: {os.path.basename(video_path)}")
        print(f"   📄 Subtitle: {os.path.basename(subtitle_path)}")
        
        if not os.path.exists(video_path):
            print(f"   ❌ Video file not found: {video_path}")
            return False, "video_not_found"
            
        if not os.path.exists(subtitle_path):
            print(f"   ❌ Subtitle file not found: {subtitle_path}")
            return False, "subtitle_not_found"
        
        # Check if already synced
        already_synced, synced_path = self.is_already_synced(video_path, subtitle_path)
        if already_synced and synced_path:
            print(f"   🎉 Subtitle already synced! Using: {os.path.basename(synced_path)}")
            return True, "already_synced"
        
        # Show file sizes
        try:
            subtitle_size = os.path.getsize(subtitle_path) / 1024  # KB
            video_size = os.path.getsize(video_path) / (1024**3)  # GB
            print(f"   📊 Subtitle: {subtitle_size:.1f} KB, Video: {video_size:.1f} GB")
        except:
            pass
        
        # Create backup of original
        backup_path = subtitle_path + '.backup'
        if not os.path.exists(backup_path):
            try:
                shutil.copy2(subtitle_path, backup_path)
                print(f"   💾 Backup created: {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"   ⚠️ Could not create backup: {e}")
        
        # Create synced output path
        synced_output_path = self.get_synced_subtitle_path(subtitle_path)
        
        # SIMPLIFIED ffsubsync command (remove problematic parameters)
        cmd = [
            'ffsubsync',
            video_path,                    # POSITIONAL: Reference video file
            '-i', subtitle_path,           # Input subtitle file
            '-o', synced_output_path,      # Output subtitle file
            '--vad', 'webrtc',             # Voice Activity Detection
            '--max-offset-seconds', '60'   # Maximum offset (reduced)
        ]
        
        print(f"   🔄 Running ffsubsync on Mac M1...")
        print(f"   ⚙️ Command: ffsubsync [video] -i [subtitle] -o [output]")
        print(f"   📁 Output: {os.path.basename(synced_output_path)}")
        
        try:
            # M1-optimized timeout
            timeout = max(300, int(video_size * 30) if 'video_size' in locals() else 300)
            print(f"   ⏱️ Timeout: {timeout} seconds")
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            processing_time = time.time() - start_time
            
            print(f"   ⏱️ Processing completed in {processing_time:.1f} seconds")
            print(f"   📟 Return code: {result.returncode}")
            
            if result.returncode == 0:
                # Success!
                if os.path.exists(synced_output_path) and os.path.getsize(synced_output_path) > 0:
                    print(f"   ✅ Subtitle synchronized successfully!")
                    print(f"   📁 Synced file: {os.path.basename(synced_output_path)}")
                    
                    # Extract sync info from output
                    offset = 0.0
                    if result.stdout:
                        print(f"   📊 ffsubsync output:")
                        stdout_lines = result.stdout.split('\n')
                        for line in stdout_lines[:10]:  # Show first 10 lines
                            line = line.strip()
                            if line:
                                print(f"      {line}")
                                # Try to extract offset
                                if 'offset' in line.lower() or 'shift' in line.lower():
                                    try:
                                        import re
                                        numbers = re.findall(r'-?\d+\.?\d*', line)
                                        if numbers:
                                            offset = float(numbers[0])
                                    except:
                                        pass
                    
                    if result.stderr and result.stderr.strip():
                        stderr_lines = result.stderr.split('\n')
                        print(f"   📊 Processing info:")
                        for line in stderr_lines[:5]:  # Show first 5 lines of stderr
                            line = line.strip()
                            if line and not line.startswith('WARNING'):
                                print(f"      {line}")
                    
                    # Record successful sync in database
                    self.record_sync_result(video_path, subtitle_path, synced_output_path, 
                                          True, offset, processing_time, "ffsubsync_webrtc")
                    
                    # 🚀 AUTO-ARCHIVE INTEGRATION
                    if hasattr(self, 'archive_manager') and self.archive_manager:
                        try:
                            print(f"   🗄️ Auto-archiving processed files...")
                            archive_success, archive_status = self.archive_manager.archive_subtitle_files(
                                video_path, subtitle_path
                            )
                            
                            if archive_success:
                                print(f"   ✅ Files archived successfully")
                                return True, f"success_offset_{offset:.3f}s_time_{processing_time:.1f}s_archived"
                            else:
                                print(f"   ⚠️ Archive failed: {archive_status}")
                                return True, f"success_offset_{offset:.3f}s_time_{processing_time:.1f}s_archive_failed"
                        except Exception as e:
                            print(f"   ❌ Archive error: {e}")
                            return True, f"success_offset_{offset:.3f}s_time_{processing_time:.1f}s_archive_error"
                    
                    return True, f"success_offset_{offset:.3f}s_time_{processing_time:.1f}s"
                else:
                    print(f"   ❌ No synced output file created or file is empty")
                    if result.stdout:
                        print(f"   📊 stdout: {result.stdout[:200]}...")
                    if result.stderr:
                        print(f"   📊 stderr: {result.stderr[:200]}...")
                    
                    self.record_sync_result(video_path, subtitle_path, synced_output_path, 
                                          False, 0, processing_time, "ffsubsync_no_output")
                    return False, "no_output_file"
                    
            else:
                print(f"   ❌ ffsubsync failed with return code: {result.returncode}")
                
                if result.stderr:
                    error_msg = result.stderr[:400] + "..." if len(result.stderr) > 400 else result.stderr
                    print(f"   📟 Error details:")
                    for line in error_msg.split('\n')[:5]:
                        if line.strip():
                            print(f"      {line.strip()}")
                
                if result.stdout:
                    output_msg = result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
                    print(f"   📟 Output: {output_msg}")
                
                # Try alternative VAD methods if webrtcvad failed
                if result.returncode != 0:
                    print(f"   💡 Trying alternative VAD method...")
                    return self._retry_with_alternative_vad(video_path, subtitle_path, synced_output_path, processing_time)
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ ffsubsync timed out after {timeout} seconds")
            print(f"   💡 Large file - try increasing timeout or reducing analysis window")
            self.record_sync_result(video_path, subtitle_path, synced_output_path, 
                                  False, 0, timeout, "ffsubsync_timeout")
            return False, f"timeout_{timeout}s"
            
        except Exception as e:
            print(f"   ❌ Error running ffsubsync: {e}")
            self.record_sync_result(video_path, subtitle_path, synced_output_path, 
                                  False, 0, 0, f"ffsubsync_error_{str(e)[:30]}")
            return False, f"error_{str(e)[:50]}"
    
    def _retry_with_alternative_vad(self, video_path, subtitle_path, output_path, original_time):
        """Retry with alternative VAD method"""
        print(f"   🔄 Retrying with auditok VAD...")
        
        # Try with auditok VAD (simplified)
        cmd_alt = [
            'ffsubsync',
            video_path,
            '-i', subtitle_path,
            '-o', output_path,
            '--vad', 'auditok',            # Alternative VAD
            '--max-offset-seconds', '60'   # Reduced for retry
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=300)
            processing_time = time.time() - start_time
            
            print(f"   ⏱️ Alternative VAD completed in {processing_time:.1f} seconds")
            print(f"   📟 Return code: {result.returncode}")
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"   ✅ Success with auditok VAD!")
                
                # Show some output
                if result.stdout:
                    print(f"   📊 Output:")
                    for line in result.stdout.split('\n')[:3]:
                        if line.strip():
                            print(f"      {line.strip()}")
                
                # Record successful sync
                self.record_sync_result(video_path, subtitle_path, output_path, 
                                      True, 0, processing_time, "ffsubsync_auditok")
                
                # 🚀 AUTO-ARCHIVE INTEGRATION FOR ALT VAD
                if hasattr(self, 'archive_manager') and self.archive_manager:
                    try:
                        print(f"   🗄️ Auto-archiving processed files...")
                        archive_success, archive_status = self.archive_manager.archive_subtitle_files(
                            video_path, subtitle_path
                        )
                        
                        if archive_success:
                            print(f"   ✅ Files archived successfully")
                            return True, f"success_alt_vad_time_{processing_time:.1f}s_archived"
                        else:
                            print(f"   ⚠️ Archive failed: {archive_status}")
                            return True, f"success_alt_vad_time_{processing_time:.1f}s_archive_failed"
                    except Exception as e:
                        print(f"   ❌ Archive error: {e}")
                        return True, f"success_alt_vad_time_{processing_time:.1f}s_archive_error"
                
                return True, f"success_alt_vad_time_{processing_time:.1f}s"
            else:
                print(f"   ❌ Alternative VAD also failed (code: {result.returncode})")
                
                # Try one more time with minimal options
                print(f"   🔄 Final attempt with minimal options...")
                return self._retry_minimal_command(video_path, subtitle_path, output_path)
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Alternative VAD timed out")
            return self._retry_minimal_command(video_path, subtitle_path, output_path)
        except Exception as e:
            print(f"   ❌ Alternative VAD error: {e}")
            return self._retry_minimal_command(video_path, subtitle_path, output_path)
    
    def _retry_minimal_command(self, video_path, subtitle_path, output_path):
        """Final retry with absolute minimal command"""
        print(f"   🔄 Final attempt with minimal options...")
        
        # Absolute minimal command
        cmd_minimal = [
            'ffsubsync',
            video_path,
            '-i', subtitle_path,
            '-o', output_path
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd_minimal, capture_output=True, text=True, timeout=200)
            processing_time = time.time() - start_time
            
            print(f"   ⏱️ Minimal command completed in {processing_time:.1f} seconds")
            print(f"   📟 Return code: {result.returncode}")
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"   ✅ Success with minimal command!")
                
                # Record successful sync
                self.record_sync_result(video_path, subtitle_path, output_path, 
                                      True, 0, processing_time, "ffsubsync_minimal")
                
                # 🚀 AUTO-ARCHIVE INTEGRATION FOR MINIMAL COMMAND
                if hasattr(self, 'archive_manager') and self.archive_manager:
                    try:
                        print(f"   🗄️ Auto-archiving processed files...")
                        archive_success, archive_status = self.archive_manager.archive_subtitle_files(
                            video_path, subtitle_path
                        )
                        
                        if archive_success:
                            print(f"   ✅ Files archived successfully")
                            return True, f"success_minimal_time_{processing_time:.1f}s_archived"
                        else:
                            print(f"   ⚠️ Archive failed: {archive_status}")
                            return True, f"success_minimal_time_{processing_time:.1f}s_archive_failed"
                    except Exception as e:
                        print(f"   ❌ Archive error: {e}")
                        return True, f"success_minimal_time_{processing_time:.1f}s_archive_error"
                
                return True, f"success_minimal_time_{processing_time:.1f}s"
            else:
                print(f"   ❌ All ffsubsync attempts failed")
                
                # Show final error details
                if result.stderr:
                    print(f"   📟 Final error: {result.stderr[:200]}...")
                
                # Record failed sync
                self.record_sync_result(video_path, subtitle_path, output_path, 
                                      False, 0, processing_time, "ffsubsync_all_failed")
                
                return False, "all_attempts_failed"
                
        except Exception as e:
            print(f"   ❌ Minimal command error: {e}")
            self.record_sync_result(video_path, subtitle_path, output_path, 
                                  False, 0, 0, "ffsubsync_minimal_error")
            return False, "minimal_error"
    
    def sync_movie_hybrid(self, movie_data, language="nl"):
        """Hybrid sync: Use Bazarr for discovery, Mac M1 for processing"""
        print(f"\n🎬 HYBRID SYNC: {movie_data.get('title', 'Unknown')}")
        print("=" * 60)
        
        # Step 1: Map Bazarr path to local path
        bazarr_video_path = movie_data.get('path')
        if not bazarr_video_path:
            print(f"   ❌ No video path in Bazarr data")
            return False, "no_bazarr_path"
        
        print(f"   🌐 Bazarr path: {bazarr_video_path}")
        local_video_path = self.map_bazarr_path_to_local(bazarr_video_path)
        
        if not local_video_path:
            print(f"   ❌ Could not map to local path")
            return False, "path_mapping_failed"
        
        print(f"   📁 Local path: {local_video_path}")
        
        # Check if movie already has synced subtitle
        video_base = os.path.splitext(local_video_path)[0]
        print(f"🔍 DEBUG: Checking for existing synced movie files...")
        print(f"🔍 DEBUG: Video base: {video_base}")
        
        potential_synced_files = [
            f"{video_base}.{language}.synced.srt",
            f"{video_base}.synced.{language}.srt", 
            f"{video_base}.{language}.hi.synced.srt"
        ]
        
        print(f"🔍 DEBUG: Checking {len(potential_synced_files)} potential synced files:")
        for i, synced_file in enumerate(potential_synced_files, 1):
            exists = os.path.exists(synced_file)
            print(f"🔍 DEBUG: {i}. {exists} - {synced_file}")
            if exists:
                print(f"   🎉 Movie already synced: {os.path.basename(synced_file)}")
                return True, "already_synced"
        
        # Step 2: Find matching subtitle
        subtitle_path = self.find_matching_subtitle(local_video_path, language)
        
        if not subtitle_path:
            print(f"   ❌ No subtitle found for language '{language}'")
            return False, f"no_subtitle_{language}"
        
        # Step 3: Use Mac M1 power for actual sync
        return self.sync_using_simple_method(local_video_path, subtitle_path)
    
    def show_sync_statistics(self):
        """Display sync statistics from database"""
        stats = self.get_sync_statistics()
        if not stats:
            print("   📊 No sync statistics available")
            return
        
        print(f"\n📊 SYNC STATISTICS")
        print("=" * 50)
        print(f"Total syncs: {stats['total_syncs']}")
        print(f"Successful: {stats['successful_syncs']} ({stats['success_rate']:.1f}%)")
        print(f"Average processing time: {stats['avg_processing_time']:.1f} seconds")
        if stats['first_sync']:
            print(f"First sync: {stats['first_sync']}")
        if stats['last_sync']:
            print(f"Last sync: {stats['last_sync']}")
    
    def sync_movie_hybrid(self, media_item, language="nl"):
        """Enhanced hybrid sync with auto-archive integration"""
        try:
            print(f"\n🎬 HYBRID SYNC: {media_item.get('title', 'Unknown')}")
            print("=" * 60)

            # Step 1: Map Bazarr path to local path
            bazarr_video_path = media_item.get('path')
            if not bazarr_video_path:
                print(f"   ❌ No video path in Bazarr data")
                return False, "no_bazarr_path"

            print(f"   🌐 Bazarr path: {bazarr_video_path}")
            
            # Find the actual local file using fuzzy matching
            local_video_path = self._find_local_video_file(bazarr_video_path)
            
            if not local_video_path:
                print(f"   ❌ Could not find local video file")
                return False, "local_file_not_found"
            
            print(f"   📁 Local path: {local_video_path}")
            
            # Check if movie already has synced subtitle
            video_base = os.path.splitext(local_video_path)[0]
            potential_synced_files = [
                f"{video_base}.{language}.synced.srt",
                f"{video_base}.synced.{language}.srt", 
                f"{video_base}.{language}.hi.synced.srt"
            ]
            
            for synced_file in potential_synced_files:
                if os.path.exists(synced_file):
                    print(f"   🎉 Movie already synced: {os.path.basename(synced_file)}")
                    return True, "already_synced"
            
            # Step 2: Find subtitle file
            subtitle_path = self._find_subtitle_file(local_video_path, language)
            if not subtitle_path:
                print(f"   ❌ No {language} subtitle found")
                return False, f"no_{language}_subtitle"
            
            print(f"   ✅ Found subtitle to sync: {os.path.basename(subtitle_path)}")
            
            # Step 3: Perform sync using Mac M1 processing
            print(f"   🎯 Starting Mac M1 sync process...")
            
            video_name = os.path.basename(local_video_path)
            subtitle_name = os.path.basename(subtitle_path)
            
            print(f"   📹 Video: {video_name}")
            print(f"   📄 Subtitle: {subtitle_name}")
            
            # Show file sizes
            try:
                video_size = os.path.getsize(local_video_path) / (1024**3)  # GB
                subtitle_size = os.path.getsize(subtitle_path) / 1024  # KB
                print(f"   📊 Subtitle: {subtitle_size:.1f} KB, Video: {video_size:.1f} GB")
            except:
                pass
            
            # Create backup of original subtitle
            backup_path = subtitle_path + ".backup"
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(subtitle_path, backup_path)
                print(f"   💾 Backup created: {os.path.basename(backup_path)}")
            
            # Generate output path
            output_path = subtitle_path.replace('.srt', '.synced.srt')
            
            # Run ffsubsync
            print(f"   🔄 Running ffsubsync on Mac M1...")
            success, sync_time, return_code, error_output = self._run_ffsubsync(
                local_video_path, subtitle_path, output_path
            )
            
            if success:
                print(f"   ✅ Sync completed successfully!")
                status = f"success_time_{sync_time:.1f}s"
                
                # Record sync in database
                self._record_sync_result(
                    video_path=local_video_path,
                    subtitle_path=subtitle_path,
                    output_path=output_path,
                    language=language,
                    success=True,
                    processing_time=sync_time,
                    method="hybrid_mac"
                )
                
                # 🚀 AUTO-ARCHIVE INTEGRATION
                if hasattr(self, 'archive_manager') and self.archive_manager:
                    try:
                        print(f"   🗄️ Auto-archiving processed files...")
                        archive_success, archive_status = self.archive_manager.archive_subtitle_files(
                            local_video_path, subtitle_path
                        )
                        
                        if archive_success:
                            print(f"   ✅ Files archived successfully")
                            status += "_archived"
                        else:
                            print(f"   ⚠️ Archive failed: {archive_status}")
                            status += "_archive_failed"
                            
                    except Exception as e:
                        print(f"   ⚠️ Archive error (non-critical): {e}")
                        status += "_archive_error"
                else:
                    print(f"   ⚠️ Archive manager not available")
                
                return True, status
            else:
                print(f"   ❌ ffsubsync failed with return code: {return_code}")
                if error_output:
                    print(f"   📟 Error details:")
                    for line in error_output.split('\n')[:5]:  # Show first 5 lines
                        if line.strip():
                            print(f"      {line.strip()}")
                
                # Try alternative VAD method
                print(f"   💡 Trying alternative VAD method...")
                alt_success, alt_time = self._try_alternative_vad(
                    local_video_path, subtitle_path, output_path
                )
                
                if alt_success:
                    print(f"   ✅ Success with auditok VAD!")
                    
                    # Record sync result
                    self._record_sync_result(
                        video_path=local_video_path,
                        subtitle_path=subtitle_path,
                        output_path=output_path,
                        language=language,
                        success=True,
                        processing_time=alt_time,
                        method="hybrid_alt_vad"
                    )
                    
                    status = f"success_alt_vad_time_{alt_time:.1f}s"
                    
                    # 🚀 AUTO-ARCHIVE INTEGRATION FOR ALT VAD
                    if hasattr(self, 'archive_manager') and self.archive_manager:
                        try:
                            print(f"   🗄️ Auto-archiving processed files...")
                            archive_success, archive_status = self.archive_manager.archive_subtitle_files(
                                local_video_path, subtitle_path
                            )
                            
                            if archive_success:
                                print(f"   ✅ Files archived successfully")
                                status += "_archived"
                            else:
                                print(f"   ⚠️ Archive failed: {archive_status}")
                        except Exception as e:
                            print(f"   ⚠️ Archive error: {e}")
                    
                    return True, status
                else:
                    return False, f"sync_failed_code_{return_code}"
                    
        except Exception as e:
            self.logger.error(f"Hybrid sync error: {e}")
            return False, f"sync_error: {str(e)}"

    def _find_local_video_file(self, bazarr_path):
        """Find local video file using fuzzy matching"""
        # Extract filename from Bazarr path
        bazarr_filename = os.path.basename(bazarr_path)
        
        print(f"   🔍 Searching for file: {bazarr_filename}")
        
        # Map Bazarr path to local base path
        local_path = self.map_bazarr_path_to_local(bazarr_path)
        
        if local_path and os.path.exists(local_path):
            print(f"   ✅ Direct match found: {local_path}")
            return local_path
        
        # Try fuzzy matching in the directory
        if local_path:
            local_dir = os.path.dirname(local_path)
            if os.path.exists(local_dir):
                for file in os.listdir(local_dir):
                    if file.lower().endswith(('.mkv', '.mp4', '.avi', '.m4v', '.mov')):
                        # Check if filenames are similar
                        if self._files_match(bazarr_filename, file):
                            fuzzy_path = os.path.join(local_dir, file)
                            print(f"   ✅ Fuzzy match found: {fuzzy_path}")
                            return fuzzy_path
        
        return None

    def _files_match(self, bazarr_filename, local_filename):
        """Check if two filenames are similar enough to be the same file"""
        # Remove extensions and normalize
        bazarr_base = os.path.splitext(bazarr_filename)[0].lower()
        local_base = os.path.splitext(local_filename)[0].lower()
        
        # Simple similarity check
        return bazarr_base == local_base or bazarr_base in local_base or local_base in bazarr_base

    def _find_subtitle_file(self, video_path, language):
        """Find subtitle file for the video"""
        video_dir = os.path.dirname(video_path)
        video_base = os.path.splitext(os.path.basename(video_path))[0]
        
        # Common subtitle patterns
        patterns = [
            f"{video_base}.{language}.srt",
            f"{video_base}.{language}.sub",
            f"{video_base}.srt",
            f"{video_base}.sub"
        ]
        
        for pattern in patterns:
            subtitle_path = os.path.join(video_dir, pattern)
            if os.path.exists(subtitle_path):
                return subtitle_path
        
        return None

    def _run_ffsubsync(self, video_path, subtitle_path, output_path):
        """Run ffsubsync command"""
        import subprocess
        import time
        
        cmd = [
            "ffsubsync",
            video_path,
            "-i", subtitle_path,
            "-o", output_path,
            "--max-subtitle-seconds", "600",
            "--start-seconds", "0"
        ]
        
        print(f"   ⚙️ Command: ffsubsync [video] -i [subtitle] -o [output]")
        print(f"   📁 Output: {os.path.basename(output_path)}")
        print(f"   ⏱️ Timeout: 300 seconds")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            processing_time = time.time() - start_time
            print(f"   ⏱️ Processing completed in {processing_time:.1f} seconds")
            print(f"   📟 Return code: {result.returncode}")
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, processing_time, result.returncode, None
            else:
                return False, processing_time, result.returncode, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, 300, -1, "Timeout expired"
        except Exception as e:
            return False, 0, -1, str(e)

    def _try_alternative_vad(self, video_path, subtitle_path, output_path):
        """Try alternative VAD method (auditok)"""
        import subprocess
        import time
        
        print(f"   🔄 Retrying with auditok VAD...")
        
        cmd = [
            "ffsubsync",
            video_path,
            "-i", subtitle_path,
            "-o", output_path,
            "--vad", "auditok",
            "--max-subtitle-seconds", "600"
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # Longer timeout for alt VAD
            )
            
            processing_time = time.time() - start_time
            print(f"   ⏱️ Alternative VAD completed in {processing_time:.1f} seconds")
            print(f"   📟 Return code: {result.returncode}")
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, processing_time
            else:
                return False, processing_time
                
        except Exception as e:
            return False, 0

    def _record_sync_result(self, video_path, subtitle_path, output_path, language, success, processing_time, method):
        """Record sync result in database"""
        if not hasattr(self, 'conn') or not self.conn:
            return
        
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.conn.execute("""
                INSERT INTO sync_history 
                (video_path, subtitle_path, output_path, language, success, processing_time, method, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (video_path, subtitle_path, output_path, language, success, processing_time, method, timestamp))
            
            self.conn.commit()
            print(f"   📊 Sync result recorded in database")
            
        except Exception as e:
            print(f"   ⚠️ Could not record sync result: {e}")