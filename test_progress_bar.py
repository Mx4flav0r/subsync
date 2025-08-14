#!/usr/bin/env python3
"""
Test the ffsubsync progress bar functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.append('.')

def test_progress_bar():
    """Test the progress bar display"""
    print("🧪 TESTING PROGRESS BAR DISPLAY")
    print("=" * 50)
    
    # Simulate progress updates
    import time
    
    def update_progress(current, total, stage):
        """Simulate the progress bar update"""
        if total > 0:
            percentage = min(100, (current / total) * 100)
            # Create progress bar
            bar_length = 30
            filled_length = int(bar_length * percentage / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Print progress (with carriage return to overwrite)
            print(f"\r   📊 Progress: [{bar}] {percentage:.1f}% - {stage}", end='', flush=True)
        else:
            print(f"\r   📊 {stage}", end='', flush=True)
    
    print("Simulating ffsubsync progress...")
    
    # Simulate different stages
    stages = [
        (0, 100, "Starting..."),
        (10, 100, "Extracting speech segments..."),
        (25, 100, "Processing audio..."),
        (50, 100, "Processing audio..."),
        (75, 100, "Aligning subtitles..."),
        (90, 100, "Processing audio..."),
        (100, 100, "Complete!")
    ]
    
    for current, total, stage in stages:
        update_progress(current, total, stage)
        time.sleep(0.5)  # Simulate processing time
    
    print("\n✅ Progress bar test complete!")

if __name__ == "__main__":
    test_progress_bar()
