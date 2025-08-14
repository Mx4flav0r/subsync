"""
Archive Manager - Handles archiving and restoring of subtitle files
"""

import os
import shutil
import time
import sqlite3
from pathlib import Path

def get_logger(name):
    """Simple logger fallback"""
    import logging
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

class ArchiveManager:
    def __init__(self):
        self.logger = get_logger('ArchiveManager')
        
        # Archive directory (in user's home)
        self.archive_base = os.path.expanduser("~/subtitle_archive")
        self.archive_db = os.path.join(self.archive_base, "archive_index.db")
        
        # Create archive structure
        self.init_archive_structure()
        self.init_archive_database()
        
        # Verify permissions on startup
        self._check_archive_permissions()
    
    def _check_archive_permissions(self):
        """Check and attempt to fix archive directory permissions"""
        try:
            # Test if we can write to the archive directory
            test_file = os.path.join(self.archive_base, ".permission_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except PermissionError:
            print(f"   ⚠️ Archive directory permission issue detected!")
            print(f"   💡 To fix, run: sudo chown -R $USER {self.archive_base}")
            print(f"   💡 Or manually: chmod 755 {self.archive_base}")
        except Exception:
            pass  # Other errors are not permission-related
    
    def init_archive_structure(self):
        """Initialize archive directory structure with proper permissions"""
        try:
            # Create directories with explicit permissions (0o755 = rwxr-xr-x)
            os.makedirs(self.archive_base, mode=0o755, exist_ok=True)
            os.makedirs(os.path.join(self.archive_base, "originals"), mode=0o755, exist_ok=True)
            os.makedirs(os.path.join(self.archive_base, "backups"), mode=0o755, exist_ok=True)
            
            # Ensure directories are writable by the current user
            os.chmod(self.archive_base, 0o755)
            os.chmod(os.path.join(self.archive_base, "originals"), 0o755)
            os.chmod(os.path.join(self.archive_base, "backups"), 0o755)
            
            print(f"   📦 Archive initialized: {self.archive_base}")
        except PermissionError as e:
            print(f"   ❌ Permission error creating archive directory: {e}")
            print(f"   💡 Try running: sudo chown -R $USER {self.archive_base}")
        except Exception as e:
            print(f"   ⚠️ Could not create archive directory: {e}")
            print(f"   💡 Please ensure {self.archive_base} is writable")
    
    def init_archive_database(self):
        """Initialize SQLite database for archive tracking"""
        try:
            self.conn = sqlite3.connect(self.archive_db)
            
            # Create archive tracking table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS archived_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_path TEXT NOT NULL,
                    archive_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,  -- 'original' or 'backup'
                    video_file TEXT,
                    archive_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    md5_hash TEXT,
                    synced_file_path TEXT,
                    UNIQUE(original_path, file_type)
                )
            """)
            
            self.conn.commit()
            print(f"   📊 Archive database initialized: {self.archive_db}")
            
        except Exception as e:
            print(f"   ⚠️ Could not initialize archive database: {e}")
            self.conn = None
    
    def get_file_hash(self, file_path):
        """Get MD5 hash of file"""
        try:
            import hashlib
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except:
            return None
    
    def archive_subtitle_files(self, video_path, subtitle_path):
        """Archive original and backup subtitle files, keeping only synced version"""
        if not os.path.exists(subtitle_path):
            return False, "subtitle_not_found"
        
        video_name = os.path.basename(video_path) if video_path else "unknown"
        subtitle_dir = os.path.dirname(subtitle_path)
        subtitle_base = os.path.splitext(os.path.basename(subtitle_path))[0]
        
        archived_files = []
        
        try:
            # 1. Archive original subtitle file
            if os.path.exists(subtitle_path) and not '.synced.' in subtitle_path:
                archive_result = self._archive_single_file(
                    subtitle_path, "original", video_name, video_path
                )
                if archive_result:
                    archived_files.append(('original', subtitle_path, archive_result))
            
            # 2. Archive backup file
            backup_path = subtitle_path + '.backup'
            if os.path.exists(backup_path):
                archive_result = self._archive_single_file(
                    backup_path, "backup", video_name, video_path
                )
                if archive_result:
                    archived_files.append(('backup', backup_path, archive_result))
            
            # 3. Check for synced file
            synced_path = self._get_synced_path(subtitle_path)
            synced_exists = os.path.exists(synced_path)
            
            if archived_files and synced_exists:
                print(f"   📦 Archived {len(archived_files)} files:")
                for file_type, original, archive_path in archived_files:
                    print(f"      • {file_type}: {os.path.basename(original)} -> archive")
                
                print(f"   ✅ Keeping synced file: {os.path.basename(synced_path)}")
                return True, f"archived_{len(archived_files)}_files"
            
            elif not synced_exists:
                print(f"   ⚠️ No synced file found - restoring original files")
                # Restore if no synced version exists
                for file_type, original, archive_path in archived_files:
                    self._restore_single_file(archive_path, original)
                return False, "no_synced_file"
            
            return True, "archive_complete"
            
        except Exception as e:
            print(f"   ❌ Error archiving files: {e}")
            # Restore any files we managed to archive if there was an error
            for file_type, original, archive_path in archived_files:
                try:
                    self._restore_single_file(archive_path, original)
                except:
                    pass
            return False, f"archive_error_{str(e)[:30]}"
    
    def _archive_single_file(self, file_path, file_type, video_name, video_path):
        """Archive a single file"""
        try:
            # Create unique archive filename
            timestamp = int(time.time())
            file_name = os.path.basename(file_path)
            archive_filename = f"{timestamp}_{file_name}"
            
            archive_subdir = os.path.join(self.archive_base, file_type + "s")
            archive_path = os.path.join(archive_subdir, archive_filename)
            
            # Move file to archive
            shutil.move(file_path, archive_path)
            
            # Record in database
            if self.conn:
                file_size = os.path.getsize(archive_path)
                file_hash = self.get_file_hash(archive_path)
                synced_path = self._get_synced_path(file_path.replace('.backup', ''))
                
                self.conn.execute("""
                    INSERT OR REPLACE INTO archived_files 
                    (original_path, archive_path, file_type, video_file, file_size, md5_hash, synced_file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (file_path, archive_path, file_type, video_path, file_size, file_hash, synced_path))
                
                self.conn.commit()
            
            return archive_path
            
        except PermissionError as e:
            print(f"   ❌ Permission denied archiving {file_path}: {e}")
            print(f"   💡 Fix with: sudo chown -R $USER {self.archive_base}")
            return None
        except Exception as e:
            print(f"   ❌ Error archiving {file_path}: {e}")
            return None
    
    def _get_synced_path(self, subtitle_path):
        """Get the synced version path for a subtitle file"""
        if '.backup' in subtitle_path:
            subtitle_path = subtitle_path.replace('.backup', '')
        
        base_path = os.path.splitext(subtitle_path)[0]
        return f"{base_path}.synced.srt"
    
    def _restore_single_file(self, archive_path, original_path):
        """Restore a single file from archive"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            
            # Move file back
            shutil.move(archive_path, original_path)
            
            # Remove from database
            if self.conn:
                self.conn.execute("DELETE FROM archived_files WHERE archive_path = ?", (archive_path,))
                self.conn.commit()
            
            return True
        except Exception as e:
            print(f"   ❌ Error restoring {archive_path}: {e}")
            return False
    
    def get_archived_files(self, limit=50):
        """Get list of archived files"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.execute("""
                SELECT original_path, archive_path, file_type, video_file, 
                       archive_timestamp, file_size, synced_file_path
                FROM archived_files 
                ORDER BY archive_timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            return cursor.fetchall()
        except Exception as e:
            print(f"   ❌ Error getting archived files: {e}")
            return []
    
    def restore_files_by_video(self, video_path):
        """Restore all files for a specific video"""
        if not self.conn:
            return False, "no_database"
        
        try:
            # Get archived files for this video
            cursor = self.conn.execute("""
                SELECT original_path, archive_path, file_type 
                FROM archived_files 
                WHERE video_file = ?
                ORDER BY file_type
            """, (video_path,))
            
            files_to_restore = cursor.fetchall()
            
            if not files_to_restore:
                return False, "no_archived_files"
            
            restored_count = 0
            for original_path, archive_path, file_type in files_to_restore:
                if os.path.exists(archive_path):
                    if self._restore_single_file(archive_path, original_path):
                        restored_count += 1
                        print(f"   ✅ Restored {file_type}: {os.path.basename(original_path)}")
                    else:
                        print(f"   ❌ Failed to restore {file_type}: {os.path.basename(original_path)}")
                else:
                    print(f"   ⚠️ Archive file not found: {archive_path}")
            
            return True, f"restored_{restored_count}_files"
            
        except Exception as e:
            print(f"   ❌ Error restoring files: {e}")
            return False, f"restore_error_{str(e)[:30]}"
    
    def get_archive_statistics(self):
        """Get archive statistics"""
        if not self.conn:
            return None
        
        try:
            cursor = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_files,
                    COUNT(CASE WHEN file_type = 'original' THEN 1 END) as original_files,
                    COUNT(CASE WHEN file_type = 'backup' THEN 1 END) as backup_files,
                    SUM(file_size) as total_size,
                    MIN(archive_timestamp) as first_archive,
                    MAX(archive_timestamp) as last_archive
                FROM archived_files
            """)
            
            result = cursor.fetchone()
            if result:
                total, originals, backups, size, first, last = result
                return {
                    'total_files': total,
                    'original_files': originals,
                    'backup_files': backups,
                    'total_size_mb': (size or 0) / (1024*1024),
                    'first_archive': first,
                    'last_archive': last
                }
        except Exception as e:
            print(f"   ❌ Error getting archive statistics: {e}")
        
        return None
    
    def cleanup_orphaned_synced_files(self):
        """Find and optionally clean up synced files with no original archived"""
        if not self.conn:
            return []
        
        try:
            # Get all synced files from archive database
            cursor = self.conn.execute("""
                SELECT DISTINCT synced_file_path 
                FROM archived_files 
                WHERE synced_file_path IS NOT NULL
            """)
            
            synced_files_in_archive = {row[0] for row in cursor.fetchall()}
            
            # Find synced files on disk
            synced_files_on_disk = []
            for root, dirs, files in os.walk("/Volumes/Data"):
                for file in files:
                    if file.endswith('.synced.srt'):
                        synced_files_on_disk.append(os.path.join(root, file))
            
            # Find orphaned synced files (no archive record)
            orphaned = []
            for synced_file in synced_files_on_disk:
                if synced_file not in synced_files_in_archive:
                    # Check if original still exists
                    original_path = synced_file.replace('.synced.srt', '.srt')
                    if not os.path.exists(original_path):
                        orphaned.append(synced_file)
            
            return orphaned
            
        except Exception as e:
            print(f"   ❌ Error finding orphaned files: {e}")
            return []
    
    def show_restore_menu(self):
        """Enhanced restore menu with 'all' option"""
        print(f"\n🔙 RESTORE ARCHIVED FILES")
        print("="*50)
        
        # Get all videos with archived files
        videos_with_files = self.get_videos_with_archived_files()
        
        if not videos_with_files:
            print("📭 No archived files found")
            return
        
        total_archived_files = sum(count for _, count in videos_with_files)
        
        print(f"📊 Summary: {len(videos_with_files)} videos, {total_archived_files} total archived files")
        print()
        print(f"📋 Videos with archived files:")
        
        for i, (video_name, file_count) in enumerate(videos_with_files, 1):
            # Truncate long video names
            display_name = video_name[:60] + "..." if len(video_name) > 60 else video_name
            print(f" {i:2d}. {display_name} ({file_count} files)")
        
        print()
        print(f"🔧 RESTORE OPTIONS:")
        print(f"   • Enter number (1-{len(videos_with_files)}) to restore specific video")
        print(f"   • Enter 'all' to restore ALL archived files (emergency restore)")
        print(f"   • Enter 'back' to return")
        
        choice = input(f"👉 Select video to restore or 'all': ").strip().lower()
        
        if choice == 'back':
            return
        elif choice == 'all':
            self._restore_all_files(videos_with_files, total_archived_files)
        else:
            try:
                video_index = int(choice) - 1
                if 0 <= video_index < len(videos_with_files):
                    video_name, file_count = videos_with_files[video_index]
                    self._restore_single_video(video_name, file_count)
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input. Use number, 'all', or 'back'")

    def _restore_all_files(self, videos_with_files, total_files):
        """Restore ALL archived files - emergency restore"""
        print(f"\n⚠️  EMERGENCY RESTORE - ALL FILES")
        print("="*50)
        print(f"📦 This will restore {total_files} files from {len(videos_with_files)} videos")
        print(f"🔄 All original and backup files will be restored to their original locations")
        print(f"⚠️  This will overwrite any existing files with the same names!")
        print()
        
        # Show what will be restored
        print(f"📋 Files to be restored:")
        for video_name, file_count in videos_with_files[:10]:  # Show first 10
            short_name = video_name[:50] + "..." if len(video_name) > 50 else video_name
            print(f"   📁 {short_name}: {file_count} files")
        
        if len(videos_with_files) > 10:
            print(f"   ... and {len(videos_with_files) - 10} more videos")
        
        print()
        print(f"🚨 WARNING: This is an emergency restore function!")
        print(f"   • Use this if something went wrong with your subtitle files")
        print(f"   • This will restore original files and may overwrite synced versions")
        print(f"   • Make sure this is what you want to do!")
        
        # Double confirmation for safety
        confirm1 = input(f"\n🔴 Type 'RESTORE' to confirm emergency restore: ").strip()
        if confirm1 != 'RESTORE':
            print("❌ Emergency restore cancelled")
            return
        
        confirm2 = input(f"🔴 Are you absolutely sure? Type 'YES' to proceed: ").strip().upper()
        if confirm2 != 'YES':
            print("❌ Emergency restore cancelled")
            return
        
        print(f"\n🚀 Starting emergency restore of {total_files} files...")
        
        import time
        start_time = time.time()
        restored_count = 0
        failed_count = 0
        
        # Progress tracking
        processed_videos = 0
        
        for video_name, file_count in videos_with_files:
            processed_videos += 1
            progress = processed_videos / len(videos_with_files) * 100
            
            # Progress bar
            bar_length = 30
            filled = int(bar_length * processed_videos // len(videos_with_files))
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\n📺 [{bar}] {progress:.1f}% - Video {processed_videos}/{len(videos_with_files)}")
            print(f"   🎬 {video_name[:50]}...")
            
            # Get archived files for this video
            archived_files = self.get_archived_files_for_video(video_name)
            
            video_restored = 0
            video_failed = 0
            
            for archived_file in archived_files:
                archive_path = archived_file['archive_path']
                original_path = archived_file['original_path']
                file_type = archived_file['file_type']
                
                success, message = self.restore_single_file(archive_path, original_path, file_type)
                
                if success:
                    video_restored += 1
                    restored_count += 1
                    print(f"      ✅ {os.path.basename(original_path)}")
                else:
                    video_failed += 1
                    failed_count += 1
                    print(f"      ❌ {os.path.basename(original_path)}: {message}")
            
            print(f"   📊 Video result: {video_restored} restored, {video_failed} failed")
        
        # Final results
        total_time = time.time() - start_time
        final_bar = "█" * bar_length
        
        print(f"\n🎉 EMERGENCY RESTORE COMPLETED!")
        print("="*50)
        print(f"📊 Final Progress: [{final_bar}] 100%")
        print(f"✅ Successfully restored: {restored_count}/{total_files} files")
        print(f"❌ Failed to restore: {failed_count} files")
        print(f"📊 Success rate: {(restored_count/total_files*100):.1f}%")
        print(f"⏱️ Total time: {total_time:.1f} seconds")
        print(f"🏁 Processing speed: {total_files/total_time:.1f} files/second")
        
        if restored_count > 0:
            print(f"\n✅ Emergency restore successful!")
            print(f"💡 Check your video directories - original files have been restored")
            print(f"⚠️  You may need to re-sync subtitles if you want synced versions")
        
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} files could not be restored")
            print(f"💡 Check the archive for these files manually")

    def _restore_single_video(self, video_name, file_count):
        """Restore files for a single video with enhanced options"""
        print(f"\n🔙 RESTORE FILES FOR SINGLE VIDEO")
        print("="*50)
        print(f"🎬 Video: {video_name}")
        print(f"📦 Archived files: {file_count}")
        
        # Get detailed file list
        archived_files = self.get_archived_files_for_video(video_name)
        
        if not archived_files:
            print("❌ No archived files found for this video")
            return
        
        # Show what files are available
        print(f"\n📋 Available archived files:")
        original_files = []
        backup_files = []
        
        for i, archived_file in enumerate(archived_files, 1):
            file_type = archived_file['file_type']
            original_path = archived_file['original_path']
            archive_date = archived_file['archive_timestamp']
            
            filename = os.path.basename(original_path)
            
            if file_type == 'original':
                original_files.append((i, archived_file))
                print(f" {i:2d}. 📄 {filename} (original, {archive_date})")
            else:
                backup_files.append((i, archived_file))
                print(f" {i:2d}. 💾 {filename} (backup, {archive_date})")
        
        print(f"\n🔧 RESTORE OPTIONS:")
        print(f"   • Enter specific numbers: '1,3,5' or '1-4'")
        print(f"   • Enter 'originals' to restore only original files ({len(original_files)} files)")
        print(f"   • Enter 'backups' to restore only backup files ({len(backup_files)} files)")
        print(f"   • Enter 'all' to restore all files ({len(archived_files)} files)")
        print(f"   • Enter 'back' to return")
        
        choice = input(f"👉 Select files to restore: ").strip().lower()
        
        if choice == 'back':
            return
        elif choice == 'all':
            files_to_restore = archived_files
        elif choice == 'originals':
            files_to_restore = [f[1] for f in original_files]
        elif choice == 'backups':
            files_to_restore = [f[1] for f in backup_files]
        else:
            # Parse selection
            selected_indices = self._parse_file_selection(choice, len(archived_files))
            if selected_indices is None:
                return
            files_to_restore = [archived_files[i] for i in selected_indices]
        
        if not files_to_restore:
            print("❌ No files selected")
            return
        
        # Confirm restore
        print(f"\n⚠️  RESTORE CONFIRMATION")
        print(f"📦 Files to restore: {len(files_to_restore)}")
        for f in files_to_restore[:5]:  # Show first 5
            print(f"   📁 {os.path.basename(f['original_path'])}")
        if len(files_to_restore) > 5:
            print(f"   ... and {len(files_to_restore) - 5} more files")
        
        print(f"\n⚠️  This will overwrite existing files with the same names!")
        confirm = input(f"🔄 Restore {len(files_to_restore)} files? (y/N): ").lower()
        
        if confirm != 'y':
            print("❌ Restore cancelled")
            return
        
        # Perform restore with progress
        print(f"\n🔄 Restoring {len(files_to_restore)} files...")
        
        restored_count = 0
        failed_count = 0
        
        for i, archived_file in enumerate(files_to_restore, 1):
            archive_path = archived_file['archive_path']
            original_path = archived_file['original_path']
            file_type = archived_file['file_type']
            
            # Progress indicator
            progress = i / len(files_to_restore) * 100
            bar_length = 20
            filled = int(bar_length * i // len(files_to_restore))
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"📁 [{bar}] {progress:.0f}% - {os.path.basename(original_path)}...")
            
            success, message = self.restore_single_file(archive_path, original_path, file_type)
            
            if success:
                restored_count += 1
                print(f"   ✅ Restored successfully")
            else:
                failed_count += 1
                print(f"   ❌ Failed: {message}")
        
        # Final results
        final_bar = "█" * bar_length
        print(f"\n📊 RESTORE COMPLETED [{final_bar}] 100%")
        print(f"✅ Successfully restored: {restored_count}/{len(files_to_restore)} files")
        print(f"❌ Failed to restore: {failed_count} files")
        
        if restored_count > 0:
            print(f"🎉 Files restored to their original locations!")

    def _parse_file_selection(self, selection, max_items):
        """Parse file selection (same as menu selection but for files)"""
        if not selection:
            return None
        
        indices = []
        
        try:
            parts = selection.split(',')
            for part in parts:
                part = part.strip()
                
                if '-' in part:
                    # Range like 1-5
                    start, end = part.split('-', 1)
                    start = int(start.strip()) - 1  # Convert to 0-based
                    end = int(end.strip()) - 1
                    if 0 <= start <= end < max_items:
                        indices.extend(range(start, end + 1))
                else:
                    # Single number
                    index = int(part) - 1  # Convert to 0-based
                    if 0 <= index < max_items:
                        indices.append(index)
            
            # Remove duplicates and sort
            indices = sorted(list(set(indices)))
            return indices
            
        except ValueError:
            print("❌ Invalid selection format")
            return None

    def get_videos_with_archived_files(self):
        """Get list of videos that have archived files"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.execute("""
                SELECT video_name, COUNT(*) as file_count
                FROM archived_files 
                GROUP BY video_name
                ORDER BY MAX(archive_timestamp) DESC
            """)
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error getting videos with archived files: {e}")
            return []

    def get_archived_files_for_video(self, video_name):
        """Get all archived files for a specific video"""
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.execute("""
                SELECT archive_path, original_path, file_type, archive_timestamp
                FROM archived_files 
                WHERE video_name = ?
                ORDER BY archive_timestamp DESC
            """, (video_name,))
            
            results = cursor.fetchall()
            
            # Convert to list of dicts for easier handling
            archived_files = []
            for archive_path, original_path, file_type, timestamp in results:
                archived_files.append({
                    'archive_path': archive_path,
                    'original_path': original_path,
                    'file_type': file_type,
                    'archive_timestamp': timestamp
                })
            
            return archived_files
            
        except Exception as e:
            print(f"❌ Error getting archived files for video: {e}")
            return []

    def restore_single_file(self, archive_path, original_path, file_type):
        """Restore a single file from archive"""
        try:
            if not os.path.exists(archive_path):
                return False, "Archive file not found"
            
            # Create directory if it doesn't exist
            original_dir = os.path.dirname(original_path)
            if not os.path.exists(original_dir):
                os.makedirs(original_dir, exist_ok=True)
            
            # Copy file back
            import shutil
            shutil.copy2(archive_path, original_path)
            
            # Verify copy
            if os.path.exists(original_path):
                return True, "Restored successfully"
            else:
                return False, "Copy failed - file not created"
                
        except Exception as e:
            return False, f"Error: {str(e)}"