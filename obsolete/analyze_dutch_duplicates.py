#!/usr/bin/env python3
"""
Analyze Dutch subtitle files to find duplicates
"""

import os
import re
from collections import defaultdict

def analyze_dutch_subtitles(base_path):
    """Find directories with multiple Dutch subtitle files for the same video"""
    
    results = {
        'total_nl_files': 0,
        'directories_with_multiples': [],
        'duplicate_count': 0,
        'examples': []
    }
    
    print(f"🔍 Analyzing Dutch subtitles in: {base_path}")
    print("="*60)
    
    for root, dirs, files in os.walk(base_path):
        # Group subtitle files by their base name (without .nl.srt extension)
        subtitle_groups = defaultdict(list)
        
        for file in files:
            if file.endswith('.nl.srt'):
                results['total_nl_files'] += 1
                
                # Extract base name (remove various subtitle patterns)
                base_name = file
                # Remove .nl.srt, .nl.synced.srt, .nl.backup, etc.
                base_name = re.sub(r'\.nl\.(srt|synced\.srt|backup)$', '', base_name)
                base_name = re.sub(r'\.nl\.srt\.backup$', '', base_name)
                
                subtitle_groups[base_name].append(file)
        
        # Check for groups with multiple files
        for base_name, subtitle_files in subtitle_groups.items():
            if len(subtitle_files) > 1:
                results['duplicate_count'] += len(subtitle_files) - 1
                
                directory_info = {
                    'directory': root,
                    'base_name': base_name,
                    'files': subtitle_files,
                    'count': len(subtitle_files)
                }
                
                results['directories_with_multiples'].append(directory_info)
                
                # Keep first 10 examples for detailed output
                if len(results['examples']) < 10:
                    results['examples'].append(directory_info)
    
    return results

def print_results(results, media_type):
    """Print analysis results"""
    print(f"\n📊 {media_type.upper()} ANALYSIS RESULTS")
    print("="*60)
    print(f"📄 Total Dutch subtitle files: {results['total_nl_files']}")
    print(f"📁 Directories with multiple files: {len(results['directories_with_multiples'])}")
    print(f"🔄 Total duplicate files: {results['duplicate_count']}")
    
    if results['examples']:
        print(f"\n📋 Examples of directories with multiple Dutch subtitles:")
        print("-"*60)
        
        for i, example in enumerate(results['examples'], 1):
            rel_path = example['directory'].replace('/Volumes/Data/', '')
            print(f"\n{i}. {rel_path}")
            print(f"   Base: {example['base_name']}")
            print(f"   Files ({example['count']}):")
            for file in example['files']:
                print(f"     • {file}")

def main():
    """Main analysis function"""
    print("🎬 DUTCH SUBTITLE DUPLICATE ANALYSIS")
    print("="*60)
    
    # Analyze Movies
    if os.path.exists("/Volumes/Data/Movies"):
        movie_results = analyze_dutch_subtitles("/Volumes/Data/Movies")
        print_results(movie_results, "Movies")
    
    # Analyze TV Shows  
    if os.path.exists("/Volumes/Data/TVShows"):
        tv_results = analyze_dutch_subtitles("/Volumes/Data/TVShows")
        print_results(tv_results, "TV Shows")
    
    # Summary
    print(f"\n🎯 OVERALL SUMMARY")
    print("="*60)
    total_files = movie_results['total_nl_files'] + tv_results['total_nl_files']
    total_dirs_with_multiples = len(movie_results['directories_with_multiples']) + len(tv_results['directories_with_multiples'])
    total_duplicates = movie_results['duplicate_count'] + tv_results['duplicate_count']
    
    print(f"📄 Total Dutch subtitle files: {total_files}")
    print(f"📁 Total directories with duplicates: {total_dirs_with_multiples}")
    print(f"🔄 Total duplicate files: {total_duplicates}")
    
    if total_duplicates > 0:
        print(f"\n💡 Potential sync work: {total_duplicates} duplicate Dutch subtitles could be processed")
    else:
        print(f"\n✅ Great! No duplicate Dutch subtitle files found")

if __name__ == "__main__":
    main()
