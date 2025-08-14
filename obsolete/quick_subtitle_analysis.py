#!/usr/bin/env python3
"""Quick Dutch subtitle analysis"""

import os
import subprocess

def quick_analysis():
    print("🎬 QUICK DUTCH SUBTITLE ANALYSIS")
    print("="*50)
    
    # Count files in main directories
    def count_files(path, pattern):
        try:
            result = subprocess.run(['find', path, '-name', pattern], capture_output=True, text=True, timeout=30)
            return len([line for line in result.stdout.strip().split('\n') if line])
        except:
            return 0
    
    # Count current Dutch subtitle files
    movies_count = count_files('/Volumes/Data/Movies', '*.nl.srt')
    tv_count = count_files('/Volumes/Data/TVShows', '*.nl.srt')
    
    # Count synced files
    movies_synced = count_files('/Volumes/Data/Movies', '*.nl.synced.srt')
    tv_synced = count_files('/Volumes/Data/TVShows', '*.nl.synced.srt')
    
    # Count archived files  
    archived_count = count_files('/Users/adminvv/subtitle_archive', '*.nl.srt')
    
    print(f"📊 CURRENT STATUS:")
    print(f"   🎬 Movies - Dutch subtitles: {movies_count}")
    print(f"   📺 TV Shows - Dutch subtitles: {tv_count}")
    print(f"   🎬 Movies - Synced files: {movies_synced}")
    print(f"   📺 TV Shows - Synced files: {tv_synced}")
    print(f"   📦 Archived Dutch files: {archived_count}")
    
    total_current = movies_count + tv_count
    total_synced = movies_synced + tv_synced
    
    print(f"\n📈 SUMMARY:")
    print(f"   📄 Total current Dutch subtitles: {total_current}")
    print(f"   ✅ Total synced files: {total_synced}")
    print(f"   📦 Total archived (originals): {archived_count}")
    print(f"   🔄 Files processed: {archived_count}")
    
    # Estimate work potential
    unsynced = total_current - total_synced
    print(f"   🎯 Potential sync candidates: {unsynced}")
    
    if archived_count > 0:
        print(f"\n💡 ANALYSIS:")
        print(f"   • {archived_count} Dutch subtitles have been processed")
        print(f"   • These were likely duplicates or unsynced files")
        print(f"   • Your system has been actively syncing subtitles!")

if __name__ == "__main__":
    quick_analysis()
