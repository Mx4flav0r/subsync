#!/bin/bash

# =============================================================================
# Enhanced Subtitle Sync System - Cleanup Script (macOS/Linux)
# Move obsolete and debug files to 'obsolete' folder
# =============================================================================

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    📦 PROJECT CLEANUP SCRIPT 📦                               ${NC}"
    echo -e "${BLUE}                   Moving obsolete files to 'obsolete' folder                  ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

print_status() {
    echo -e "${GREEN}[MOVED]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
}

# Create obsolete directory
create_obsolete_dir() {
    if [[ ! -d "obsolete" ]]; then
        mkdir -p "obsolete"
        print_info "Created 'obsolete' directory"
    else
        print_info "'obsolete' directory already exists"
    fi
}

# Move file to obsolete folder if it exists
move_if_exists() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        mv "$file" "obsolete/"
        print_status "$file → obsolete/ ($description)"
        return 0
    else
        print_warning "$file not found"
        return 1
    fi
}

# Main cleanup function
main() {
    print_header
    
    echo -e "${CYAN}This script will move obsolete and debug files to an 'obsolete' folder.${NC}"
    echo -e "${CYAN}Files will be preserved for reference but removed from the main directory.${NC}"
    echo ""
    
    read -p "Continue with cleanup? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleanup cancelled by user"
        exit 0
    fi
    
    # Create obsolete directory
    create_obsolete_dir
    
    print_info "Moving debug and test files..."
    
    # Debug files
    move_if_exists "simple_debug.py" "Simple debug utility"
    move_if_exists "debug_bazarr.py" "Bazarr debug script"
    move_if_exists "debug_credentials.py" "Credential debug script"
    move_if_exists "debug_bazarr_direct.py" "Direct Bazarr debug script"
    
    # Test files
    move_if_exists "test_pagination.py" "Pagination test"
    move_if_exists "test_database.py" "Database test"
    move_if_exists "test_bazarr_api.py" "Bazarr API test"
    move_if_exists "test_bazarr.py" "Bazarr test"
    move_if_exists "test_credentials.py" "Credentials test"
    move_if_exists "test_fixes.py" "Fixes test"
    move_if_exists "test_slice.py" "Slice test"
    
    print_info "Moving obsolete/duplicate files..."
    
    # Obsolete files
    move_if_exists "bazarr_integration.py" "Old Bazarr integration (replaced by bazarr.py)"
    move_if_exists "ssh_tunnel_manager.py" "SSH tunnel manager (unused feature)"
    move_if_exists "update_bazarr_url.py" "URL update utility (one-time use)"
    move_if_exists "SETUP.md" "Old setup guide (replaced by README.md)"
    
    print_info "Moving backup and temporary database files..."
    
    # Backup files
    move_if_exists "bazarr_sync_tracking.db.backup" "Database backup"
    move_if_exists "subsync.db.backup" "Database backup"
    move_if_exists "test_write.db" "Test database"
    
    # Count moved files
    moved_count=$(ls -1 obsolete/ 2>/dev/null | wc -l)
    
    echo ""
    print_header
    print_info "🎉 Cleanup completed!"
    echo ""
    echo -e "${GREEN}Summary:${NC}"
    echo -e "${CYAN}• Files moved to 'obsolete' folder: $moved_count${NC}"
    echo -e "${CYAN}• Main directory is now cleaner and more organized${NC}"
    echo -e "${CYAN}• All files are preserved in 'obsolete' folder for reference${NC}"
    echo ""
    echo -e "${YELLOW}Note: You can safely delete the 'obsolete' folder if you don't need these files${NC}"
    echo ""
}

# Run main function
main "$@"
