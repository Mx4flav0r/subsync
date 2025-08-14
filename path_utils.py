#!/usr/bin/env python3
"""
Path Mapping Utilities
Helper functions for managing environment-specific path mappings
"""

from config import config
import os

def get_current_environment_paths():
    """Get the current environment path configuration"""
    current_env = config.get("current_environment", "mac_local")
    env_paths = config.get("environment_paths", {})
    
    if current_env in env_paths:
        return env_paths[current_env]
    
    # Fallback to legacy configuration
    return {
        "movies_local": "/Volumes/Data/Movies",
        "movies_plex": "/PlexMedia/Movies",
        "series_local": "/Volumes/Data/TVShows", 
        "series_plex": "/PlexMedia/TVShows",
        "description": "Fallback configuration"
    }

def convert_local_path_to_plex_path(local_path):
    """Convert a local path to the corresponding Plex path"""
    env_paths = get_current_environment_paths()
    
    # Try to match against configured paths
    if local_path.startswith(env_paths.get("movies_local", "")):
        relative_path = local_path.replace(env_paths["movies_local"], "")
        return env_paths.get("movies_plex", "") + relative_path
    
    if local_path.startswith(env_paths.get("series_local", "")):
        relative_path = local_path.replace(env_paths["series_local"], "")
        return env_paths.get("series_plex", "") + relative_path
    
    # Fallback to legacy path mappings
    path_mappings = config.get("path_mappings", {})
    for plex_path, mapped_local_path in path_mappings.items():
        if local_path.startswith(mapped_local_path):
            relative_path = local_path.replace(mapped_local_path, "")
            return plex_path + relative_path
    
    # Return original path if no mapping found
    return local_path

def convert_plex_path_to_local_path(plex_path):
    """Convert a Plex path to the corresponding local path"""
    env_paths = get_current_environment_paths()
    
    # Try to match against configured paths
    if plex_path.startswith(env_paths.get("movies_plex", "")):
        relative_path = plex_path.replace(env_paths["movies_plex"], "")
        return env_paths.get("movies_local", "") + relative_path
    
    if plex_path.startswith(env_paths.get("series_plex", "")):
        relative_path = plex_path.replace(env_paths["series_plex"], "")
        return env_paths.get("series_local", "") + relative_path
    
    # Fallback to legacy path mappings
    path_mappings = config.get("path_mappings", {})
    for mapped_plex_path, local_path in path_mappings.items():
        if plex_path.startswith(mapped_plex_path):
            relative_path = plex_path.replace(mapped_plex_path, "")
            return local_path + relative_path
    
    # Return original path if no mapping found
    return plex_path

def validate_environment_paths():
    """Validate that current environment paths are accessible"""
    env_paths = get_current_environment_paths()
    
    results = {}
    
    for path_type in ["movies_local", "series_local"]:
        path = env_paths.get(path_type)
        if path:
            results[path_type] = os.path.exists(path)
        else:
            results[path_type] = None
    
    return results

def get_environment_summary():
    """Get a summary of current environment configuration"""
    current_env = config.get("current_environment", "mac_local")
    env_paths = get_current_environment_paths()
    
    return {
        "environment": current_env,
        "description": env_paths.get("description", "No description"),
        "paths": env_paths,
        "validation": validate_environment_paths()
    }
