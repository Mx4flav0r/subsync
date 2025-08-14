#!/usr/bin/env python3
"""
Database management for the Enhanced Subtitle Sync System
"""

import sqlite3
import os

class DatabaseManager:
    def __init__(self):
        """Initialize database connections"""
        self.init_databases()
    
    def init_databases(self):
        """Initialize all required databases"""
        try:
            # Main tracking database - use local path
            db_path = "bazarr_sync_tracking.db"
            self.conn = sqlite3.connect(db_path)
            print(f"📊 Enhanced database initialized: {db_path}")
            
            # Sync history database - use local path instead of Mac-specific path
            sync_db_path = "subtitle_sync_history.db"
            self.sync_conn = sqlite3.connect(sync_db_path)
            print(f"   📊 Sync tracking database initialized: {sync_db_path}")
            
            # Create tables
            self.create_tables()
            print("📊 Database tables created successfully")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            # Set connections to None so we know they failed
            self.conn = None
            self.sync_conn = None
    
    def close_connections(self):
        """Close all database connections"""
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
            if self.sync_conn:
                self.sync_conn.close()
                self.sync_conn = None
            print("📊 Database connections closed")
        except Exception as e:
            print(f"⚠️ Error closing connections: {e}")
    
    def create_tables(self):
        """Create necessary database tables with correct schema"""
        try:
            cursor = self.conn.cursor()
            
            # Drop existing tables if they have wrong schema
            cursor.execute("DROP TABLE IF EXISTS credentials")
            cursor.execute("DROP TABLE IF EXISTS sync_history")
            
            # Create credentials table with correct schema
            cursor.execute("""
                CREATE TABLE credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL UNIQUE,
                    bazarr_url TEXT,
                    bazarr_api_key TEXT,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sync history table with language column
            cursor.execute("""
                CREATE TABLE sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_file TEXT NOT NULL,
                    subtitle_file TEXT NOT NULL,
                    output_path TEXT,
                    sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sync_method TEXT DEFAULT 'hybrid',
                    status TEXT DEFAULT 'completed',
                    processing_time REAL,
                    language TEXT DEFAULT 'nl'
                )
            """)
            
            self.conn.commit()
            print("📊 Database tables created successfully")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
        
    def save_bazarr_credentials(self, url, api_key):
        """Save Bazarr credentials to database"""
        try:
            # Use a fresh connection for this operation
            conn = sqlite3.connect("bazarr_sync_tracking.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO credentials (service, bazarr_url, bazarr_api_key, last_updated)
                VALUES ('bazarr', ?, ?, CURRENT_TIMESTAMP)
            """, (url, api_key))
            conn.commit()
            conn.close()  # Always close the connection
            print("💾 Bazarr credentials saved successfully")
            return True
        except Exception as e:
            print(f"❌ Could not save credentials: {e}")
            return False

    def load_bazarr_credentials(self):
        """Load Bazarr credentials from database"""
        try:
            # Use a fresh connection for this operation
            conn = sqlite3.connect("bazarr_sync_tracking.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bazarr_url, bazarr_api_key FROM credentials 
                WHERE service = 'bazarr' 
                ORDER BY last_updated DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            conn.close()  # Always close the connection
            
            if result:
                return result[0], result[1]  # url, api_key
            else:
                return None, None
                
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            return None, None

    def save_plex_credentials(self, url, token):
        """Save Plex credentials to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO credentials (service, bazarr_url, bazarr_api_key, last_updated)
                VALUES ('plex', ?, ?, CURRENT_TIMESTAMP)
            """, (url, token))
            self.conn.commit()
            print("💾 Plex credentials saved successfully")
            return True
        except Exception as e:
            print(f"❌ Could not save Plex credentials: {e}")
            return False

    def load_plex_credentials(self):
        """Load Plex credentials from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT bazarr_url, bazarr_api_key FROM credentials 
                WHERE service = 'plex' 
                ORDER BY last_updated DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                return result[0], result[1]  # url, token
            else:
                return None, None
                
        except Exception as e:
            print(f"❌ Error loading Plex credentials: {e}")
            return None, None

    def archive_old_subtitle(self, subtitle_file):
        """Archive old subtitle before overwriting"""
        try:
            import shutil
            from datetime import datetime
            
            # Create archive directory
            archive_dir = os.path.join(os.path.dirname(subtitle_file), "subtitle_archive")
            os.makedirs(archive_dir, exist_ok=True)
            
            # Create archived filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(subtitle_file)
            name, ext = os.path.splitext(filename)
            archived_name = f"{name}_backup_{timestamp}{ext}"
            
            # Archive the file
            archive_path = os.path.join(archive_dir, archived_name)
            shutil.copy2(subtitle_file, archive_path)
            
            print(f"      📦 Archived original: {archived_name}")
            return archive_path
            
        except Exception as e:
            print(f"      ⚠️  Could not archive subtitle: {e}")
            return None

    def is_already_synced(self, video_file, subtitle_file):
        """Check if file combination was already synced"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM sync_history 
                WHERE video_file = ? AND subtitle_file = ? AND status = 'completed'
                AND sync_timestamp > datetime('now', '-7 days')
            """, (video_file, subtitle_file))
            
            result = cursor.fetchone()
            return result[0] > 0 if result else False
            
        except Exception as e:
            print(f"      ⚠️  Could not check sync status: {e}")
            return False

    def record_sync_result(self, video_file, subtitle_file, language, processing_time, output_path):
        """Record sync result in database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sync_history 
                (video_file, subtitle_file, language, processing_time, output_path, status)
                VALUES (?, ?, ?, ?, ?, 'completed')
            """, (video_file, subtitle_file, language, processing_time, output_path))
            self.conn.commit()
        except Exception as e:
            print(f"      ⚠️  Could not record sync result: {e}")

    def get_sync_statistics(self, days=7):
        """Get sync statistics from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_syncs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_syncs,
                    AVG(processing_time) as avg_time,
                    MIN(sync_timestamp) as first_sync,
                    MAX(sync_timestamp) as last_sync
                FROM sync_history
                WHERE sync_timestamp >= datetime('now', '-{} days')
            """.format(days))
            
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
            print(f"❌ Error getting statistics: {e}")
        return None