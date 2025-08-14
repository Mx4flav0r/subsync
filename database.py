#!/usr/bin/env python3
"""
Database Management Module
Wrapper around the existing DatabaseManager with additional functionality
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

# Import your existing powerful database manager
try:
    from database_manager import DatabaseManager as CoreDatabaseManager
except ImportError:
    print("⚠️ Could not import database_manager.py - using fallback implementation")
    CoreDatabaseManager = None

class Database:
    """Enhanced database management using your existing DatabaseManager"""
    
    def __init__(self):
        self.db_path = "subsync.db"
        
        # Use your existing DatabaseManager if available
        if CoreDatabaseManager:
            self.core_db = CoreDatabaseManager()
            self.use_core = True
            print("✅ Using your existing powerful DatabaseManager")
            # Still initialize fallback database for health checks and credentials
            self._init_fallback_database()
        else:
            self.core_db = None
            self.use_core = False
            self._init_fallback_database()
            print("⚠️ Using fallback database implementation")
    
    def _init_fallback_database(self):
        """Initialize fallback database if core DB not available"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Basic tables for fallback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    service TEXT PRIMARY KEY,
                    url TEXT,
                    token TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_path TEXT NOT NULL,
                    subtitle_path TEXT NOT NULL,
                    synced_path TEXT,
                    language TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sync_time REAL,
                    offset_applied REAL,
                    method TEXT,
                    video_hash TEXT,
                    subtitle_hash TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Fallback database init error: {e}")
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = None) -> Any:
        """Execute database query with proper connection handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()
            
            conn.commit()
            conn.close()
            return result
            
        except Exception as e:
            print(f"❌ Database query error: {e}")
            return None
    
    def save_credentials(self, service: str, url: str, token: str) -> bool:
        """Save service credentials"""
        if self.use_core and hasattr(self.core_db, 'save_bazarr_credentials') and service == 'bazarr':
            return self.core_db.save_bazarr_credentials(url, token)
        elif self.use_core and hasattr(self.core_db, 'save_plex_credentials') and service == 'plex':
            return self.core_db.save_plex_credentials(url, token)
        else:
            # Fallback implementation
            return self.execute_query(
                "INSERT OR REPLACE INTO credentials (service, url, token) VALUES (?, ?, ?)",
                (service, url, token)
            ) is not None
    
    def get_credentials(self, service: str) -> Tuple[Optional[str], Optional[str]]:
        """Get service credentials"""
        if self.use_core and hasattr(self.core_db, 'load_bazarr_credentials') and service == 'bazarr':
            return self.core_db.load_bazarr_credentials()
        elif self.use_core and hasattr(self.core_db, 'load_plex_credentials') and service == 'plex':
            return self.core_db.load_plex_credentials()
        else:
            # Fallback implementation
            result = self.execute_query(
                "SELECT url, token FROM credentials WHERE service = ?",
                (service,), fetch="one"
            )
            return result if result else (None, None)
    
    def record_sync(self, video_path: str, subtitle_path: str, synced_path: str,
                   language: str, status: str, sync_time: float = 0,
                   offset: float = 0, method: str = "ffsubsync") -> bool:
        """Record sync operation"""
        if self.use_core and hasattr(self.core_db, 'record_sync_result'):
            return self.core_db.record_sync_result(
                video_path, subtitle_path, language, sync_time, synced_path
            )
        else:
            # Fallback implementation
            video_hash = self._get_file_hash(video_path)
            subtitle_hash = self._get_file_hash(subtitle_path)
            
            return self.execute_query("""
                INSERT OR REPLACE INTO sync_history 
                (video_path, subtitle_path, synced_path, language, status, 
                 sync_time, offset_applied, method, video_hash, subtitle_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (video_path, subtitle_path, synced_path, language, status,
                  sync_time, offset, method, video_hash, subtitle_hash)) is not None
    
    def is_synced(self, video_path: str, language: str) -> Tuple[bool, Optional[str]]:
        """Check if video already has synced subtitle"""
        if self.use_core and hasattr(self.core_db, 'is_already_synced'):
            # Find a subtitle file to check with
            video_dir = os.path.dirname(video_path)
            video_base = os.path.splitext(os.path.basename(video_path))[0]
            subtitle_path = os.path.join(video_dir, f"{video_base}.{language}.srt")
            
            if os.path.exists(subtitle_path):
                is_synced = self.core_db.is_already_synced(video_path, subtitle_path)
                if is_synced:
                    synced_path = os.path.join(video_dir, f"{video_base}.synced.srt")
                    return True, synced_path if os.path.exists(synced_path) else None
        
        # Fallback implementation
        video_hash = self._get_file_hash(video_path)
        result = self.execute_query("""
            SELECT synced_path, created_at FROM sync_history 
            WHERE video_path = ? AND language = ? AND video_hash = ? AND status = 'success'
            ORDER BY created_at DESC LIMIT 1
        """, (video_path, language, video_hash), fetch="one")
        
        if result and os.path.exists(result[0]):
            return True, result[0]
        return False, None
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive sync statistics"""
        if self.use_core and hasattr(self.core_db, 'get_sync_statistics'):
            return self.core_db.get_sync_statistics(days) or {}
        
        # Fallback implementation
        stats = {
            'total': 0,
            'successful': 0,
            'success_rate': 0.0,
            'avg_time': 0.0,
            'min_time': 0.0,
            'max_time': 0.0
        }
        
        try:
            # Overall stats
            result = self.execute_query("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    AVG(CASE WHEN status = 'success' THEN sync_time END) as avg_time,
                    MIN(CASE WHEN status = 'success' THEN sync_time END) as min_time,
                    MAX(CASE WHEN status = 'success' THEN sync_time END) as max_time
                FROM sync_history 
                WHERE created_at > datetime('now', '-{} days')
            """.format(days), fetch="one")
            
            if result:
                total, successful, avg_time, min_time, max_time = result
                stats['total'] = total or 0
                stats['successful'] = successful or 0
                stats['success_rate'] = (successful / total * 100) if total > 0 else 0
                stats['avg_time'] = avg_time or 0
                stats['min_time'] = min_time or 0
                stats['max_time'] = max_time or 0
        except Exception as e:
            # If sync_history table doesn't exist, return default stats
            pass
        
        return stats
    
    def flush_credentials(self) -> bool:
        """Delete all credentials"""
        try:
            return self.execute_query("DELETE FROM credentials") is not None
        except:
            return False
    
    def flush_sync_history(self) -> bool:
        """Delete all sync history"""
        try:
            return self.execute_query("DELETE FROM sync_history") is not None
        except:
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        health = {
            "database_file": os.path.exists(self.db_path),
            "core_database": self.use_core,
            "writable": True,
            "total_syncs": 0,
            "recent_syncs": 0
        }
        
        try:
            # Test write access
            self.execute_query("SELECT 1")
            
            # Count total syncs - use core database if available
            if self.use_core and hasattr(self.core_db, 'get_sync_count'):
                health["total_syncs"] = self.core_db.get_sync_count()
            else:
                # Try fallback database
                try:
                    result = self.execute_query("SELECT COUNT(*) FROM sync_history", fetch="one")
                    health["total_syncs"] = result[0] if result else 0
                except:
                    # If sync_history table doesn't exist in main db, that's okay
                    health["total_syncs"] = 0
            
        except Exception as e:
            health["writable"] = False
            health["error"] = str(e)
        
        return health
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get file hash for change detection"""
        try:
            if not os.path.exists(file_path):
                return "missing"
            
            import hashlib
            size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)
            content = f"{file_path}_{size}_{mtime}"
            return hashlib.md5(content.encode()).hexdigest()[:16]
        except:
            return "error"

# Global database instance
database = Database()
