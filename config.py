#!/usr/bin/env python3
"""
Configuration Management Module
Centralized settings and configuration for the subtitle sync system
"""

import json
import os
from typing import Dict, List, Any, Optional

class Config:
    """Centralized configuration management"""
    
    def __init__(self, config_file: str = "subsync_config.json"):
        self.config_file = config_file
        self.defaults = {
            # Bazarr Settings
            "bazarr_url": "http://192.168.90.3:30046",
            "bazarr_api_key": None,
            
            # Plex Settings  
            "plex_url": "http://192.168.90.3:32400",
            "plex_token": None,
            "plex_integration": True,
            
            # Sync Settings
            "preferred_languages": ["nl", "en"],
            "max_workers": 2,
            "sync_timeout": 300,
            "vad_method": "webrtcvad",
            
            # Path Settings
            "base_paths": [
                "/Volumes/Data/Movies",
                "/Volumes/Data/TVShows", 
                "/Volumes/Data/Christmas"
            ],
            "path_mappings": {
                "/PlexMedia/Movies": "/Volumes/Data/Movies",
                "/PlexMedia/TVShows": "/Volumes/Data/TVShows"
            },
            
            # Environment-specific Path Settings
            "current_environment": "mac_local",
            "environment_paths": {
                "mac_local": {
                    "movies_local": "/Volumes/Data/Movies",
                    "movies_plex": "/PlexMedia/Movies",
                    "series_local": "/Volumes/Data/TVShows",
                    "series_plex": "/PlexMedia/TVShows",
                    "description": "Mac M1 Local Environment"
                },
                "windows_remote": {
                    "movies_local": "\\\\192.168.90.2\\Movies",
                    "movies_plex": "/PlexMedia/Movies", 
                    "series_local": "\\\\192.168.90.2\\TVShows",
                    "series_plex": "/PlexMedia/TVShows",
                    "description": "Windows Remote Network Environment"
                },
                "docker_container": {
                    "movies_local": "/data/movies",
                    "movies_plex": "/PlexMedia/Movies",
                    "series_local": "/data/tvshows", 
                    "series_plex": "/PlexMedia/TVShows",
                    "description": "Docker Container Environment"
                }
            },
            
            # Feature Toggles
            "auto_archive": True,
            "duplicate_detection": True,
            "session_tracking": True,
            "multi_vad_fallback": True,
            
            # Advanced Settings
            "archive_directory": "~/subtitle_archive",
            "database_path": "subsync.db",
            "log_level": "INFO"
        }
        
        self.settings = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults
                    settings = self.defaults.copy()
                    settings.update(saved_settings)
                    return settings
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
        
        return self.defaults.copy()
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2, sort_keys=True)
            print(f"💾 Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value and save"""
        self.settings[key] = value
        return self.save_config()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        self.settings.update(updates)
        return self.save_config()
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        self.settings = self.defaults.copy()
        return self.save_config()
    
    def get_bazarr_config(self) -> Dict[str, str]:
        """Get Bazarr-specific configuration"""
        return {
            "url": self.get("bazarr_url"),
            "api_key": self.get("bazarr_api_key")
        }
    
    def get_plex_config(self) -> Dict[str, str]:
        """Get Plex-specific configuration"""
        return {
            "url": self.get("plex_url"),
            "token": self.get("plex_token")
        }
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Get sync-specific configuration"""
        return {
            "languages": self.get("preferred_languages"),
            "timeout": self.get("sync_timeout"),
            "vad_method": self.get("vad_method"),
            "max_workers": self.get("max_workers"),
            "auto_archive": self.get("auto_archive"),
            "duplicate_detection": self.get("duplicate_detection"),
            "multi_vad_fallback": self.get("multi_vad_fallback")
        }
    
    def get_path_config(self) -> Dict[str, Any]:
        """Get path-specific configuration"""
        return {
            "base_paths": self.get("base_paths"),
            "path_mappings": self.get("path_mappings"),
            "archive_directory": os.path.expanduser(self.get("archive_directory"))
        }
    
    def show_current_config(self):
        """Display current configuration"""
        print("\n⚙️ CURRENT CONFIGURATION")
        print("=" * 50)
        
        # Bazarr
        bazarr = self.get_bazarr_config()
        print(f"🌐 Bazarr URL: {bazarr['url']}")
        print(f"🔑 Bazarr API Key: {'✅ Set' if bazarr['api_key'] else '❌ Not set'}")
        
        # Plex
        plex = self.get_plex_config()
        print(f"🎬 Plex URL: {plex['url']}")
        print(f"🔑 Plex Token: {'✅ Set' if plex['token'] else '❌ Not set'}")
        
        # Sync
        sync = self.get_sync_config()
        print(f"🌍 Languages: {', '.join(sync['languages'])}")
        print(f"⏱️ Timeout: {sync['timeout']}s")
        print(f"🔊 VAD Method: {sync['vad_method']}")
        print(f"👥 Max Workers: {sync['max_workers']}")
        
        # Features
        print(f"📦 Auto Archive: {'✅' if sync['auto_archive'] else '❌'}")
        print(f"🔍 Duplicate Detection: {'✅' if sync['duplicate_detection'] else '❌'}")
        print(f"🔄 Multi VAD Fallback: {'✅' if sync['multi_vad_fallback'] else '❌'}")
        
        # Paths
        paths = self.get_path_config()
        print(f"📁 Base Paths: {len(paths['base_paths'])} configured")
        print(f"🗺️ Path Mappings: {len(paths['path_mappings'])} configured")
        print(f"📦 Archive Dir: {paths['archive_directory']}")

# Global config instance
config = Config()
