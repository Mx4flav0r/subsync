#!/usr/bin/env python3
"""
Main Entry Point for Enhanced Subtitle Sync System
🚀 Powered by PathMapper Engine
"""

import os
import sys
import signal
from pathlib import Path

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n👋 Interrupted by user - goodbye!")
    sys.exit(0)

def check_dependencies():
    """Check for required dependencies"""
    required_modules = [
        ('requests', 'pip install requests'),
        ('sqlite3', 'Built-in Python module'),
    ]
    
    optional_modules = [
        ('ffsubsync', 'pip install ffsubsync'),
    ]
    
    print("🔍 DEPENDENCY CHECK")
    print("=" * 40)
    
    missing_required = []
    missing_optional = []
    
    for module, install_cmd in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - {install_cmd}")
            missing_required.append((module, install_cmd))
    
    for module, install_cmd in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"⚠️  {module} (optional) - {install_cmd}")
            missing_optional.append((module, install_cmd))
    
    if missing_required:
        print(f"\n❌ Missing required dependencies:")
        for module, cmd in missing_required:
            print(f"   {module}: {cmd}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional dependencies (recommended):")
        for module, cmd in missing_optional:
            print(f"   {module}: {cmd}")
        print("   System will work but may have limited functionality")
    
    print("✅ Dependency check complete!")
    return True

def setup_environment():
    """Setup environment and working directory"""
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create necessary directories
    directories = [
        "logs",
        "backups", 
        "archive",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print(f"📁 Working directory: {os.getcwd()}")

def show_banner():
    """Show application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 ENHANCED SUBTITLE SYNC SYSTEM 🚀                      ║
║                                                                              ║
║                        💪 Powered by PathMapper Engine                       ║
║                                                                              ║
║  Features:                                                                   ║
║  • 🔥 Advanced PathMapper sync engine with fallback methods                 ║
║  • 🌐 Seamless Bazarr integration for media discovery                       ║
║  • 📦 Intelligent archive management with restore capabilities              ║
║  • 📊 Comprehensive statistics and session tracking                         ║
║  • ⚡ Parallel processing for bulk operations                               ║
║  • 🔍 Smart duplicate detection and skip logic                             ║
║  • 🎯 Multiple VAD method fallbacks for maximum compatibility               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main application entry point"""
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Show banner
        show_banner()
        
        # Setup environment
        print("🔧 INITIALIZATION")
        print("=" * 50)
        setup_environment()
        
        # Check dependencies
        if not check_dependencies():
            print("\n❌ Dependency check failed!")
            print("💡 Install missing dependencies and try again")
            return 1
        
        # Import main modules (after dependency check)
        try:
            from cli import SubtitleSyncCLI
            print("✅ All modules imported successfully")
        except ImportError as e:
            print(f"❌ Module import error: {e}")
            print("💡 Make sure all required files are present:")
            required_files = [
                "cli.py", "sync_engine.py", "config.py", "database.py",
                "bazarr.py", "path_mapper.py", "archive_manager.py"
            ]
            
            for file in required_files:
                exists = "✅" if Path(file).exists() else "❌"
                print(f"   {exists} {file}")
            
            return 1
        
        print("\n🚀 Starting Enhanced Subtitle Sync System...")
        print("💪 Powered by your PathMapper engine!")
        
        # Start the CLI
        cli = SubtitleSyncCLI()
        cli.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user - goodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\n🔍 Debug information:")
        import traceback
        traceback.print_exc()
        return 1

def quick_sync():
    """Quick sync function for direct usage"""
    try:
        from sync_engine import sync_engine
        from bazarr import bazarr
        
        print("🚀 QUICK SYNC MODE")
        print("=" * 40)
        
        if not bazarr.is_configured():
            print("❌ Bazarr not configured")
            print("💡 Run 'python main.py' for full setup")
            return False
        
        # Get all media and sync
        results = sync_engine.batch_sync_all("nl")
        
        print(f"\n🎉 QUICK SYNC RESULTS")
        print("=" * 30)
        print(f"✅ Successful: {results['successful']}")
        print(f"⭐ Skipped: {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick sync error: {e}")
        return False

def show_status():
    """Show system status"""
    try:
        from sync_engine import sync_engine
        from bazarr import bazarr
        from database import database
        
        print("📊 SYSTEM STATUS")
        print("=" * 40)
        
        # Sync engine status
        print("🔧 Sync Engine:")
        print(f"  PathMapper: {'✅' if sync_engine.use_pathmapper else '⚠️  Fallback'}")
        print(f"  Archive Manager: {'✅' if sync_engine.archive_manager else '❌'}")
        
        # Bazarr status
        print("🌐 Bazarr:")
        print(f"  Configured: {'✅' if bazarr.is_configured() else '❌'}")
        print(f"  Connected: {'✅' if bazarr.test_connection() else '❌'}")
        
        # Database status
        health = database.health_check()
        print("💾 Database:")
        print(f"  Available: {'✅' if health.get('database_file') else '❌'}")
        print(f"  Writable: {'✅' if health.get('writable') else '❌'}")
        
        # Statistics
        stats = database.get_statistics(7)
        print("📈 Recent Activity (7 days):")
        print(f"  Total syncs: {stats.get('total', 0)}")
        print(f"  Success rate: {stats.get('success_rate', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['quick', 'q']:
            sys.exit(0 if quick_sync() else 1)
        elif command in ['status', 's']:
            sys.exit(0 if show_status() else 1)
        elif command in ['help', 'h', '--help', '-h']:
            print("🚀 Enhanced Subtitle Sync System")
            print("\nUsage:")
            print("  python main.py          - Start interactive mode")
            print("  python main.py quick    - Quick sync all media")
            print("  python main.py status   - Show system status")
            print("  python main.py help     - Show this help")
            sys.exit(0)
        else:
            print(f"❌ Unknown command: {command}")
            print("💡 Use 'python main.py help' for available commands")
            sys.exit(1)
    
    # Default: start interactive mode
    sys.exit(main())
