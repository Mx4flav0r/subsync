#!/usr/bin/env python3
"""
Fix Permission Issues for Subtitle Sync System
===============================================

This script fixes common permission issues with the archive directory.
Run this if you get permission denied errors when using the archive functionality.
"""

import os
import stat
import getpass

def fix_archive_permissions():
    """Fix archive directory permissions"""
    username = getpass.getuser()
    archive_dir = os.path.expanduser("~/subtitle_archive")
    
    print(f"🔧 Fixing permissions for {archive_dir}")
    print(f"👤 Current user: {username}")
    
    if not os.path.exists(archive_dir):
        print(f"📁 Archive directory doesn't exist yet - will be created on first run")
        return
    
    try:
        # Check current ownership
        stat_info = os.stat(archive_dir)
        current_uid = stat_info.st_uid
        current_user_uid = os.getuid()
        
        if current_uid != current_user_uid:
            print(f"❌ Archive directory owned by UID {current_uid}, but you are UID {current_user_uid}")
            print(f"💡 Run this command to fix:")
            print(f"   sudo chown -R {username} {archive_dir}")
            return False
        
        # Check if writable
        if os.access(archive_dir, os.W_OK):
            print(f"✅ Archive directory permissions are correct!")
            return True
        else:
            print(f"❌ Archive directory is not writable")
            print(f"💡 Run this command to fix:")
            print(f"   chmod 755 {archive_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Subtitle Sync System - Permission Fixer")
    print("=" * 50)
    fix_archive_permissions()
