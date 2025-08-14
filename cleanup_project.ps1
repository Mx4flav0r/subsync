# =============================================================================
# Enhanced Subtitle Sync System - Cleanup Script (Windows PowerShell)
# Move obsolete and debug files to 'obsolete' folder
# =============================================================================

# Color functions
function Write-Success { param($Message) Write-Host "[MOVED] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[SKIP] $Message" -ForegroundColor Yellow }

function Write-Header {
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "                    📦 PROJECT CLEANUP SCRIPT 📦                               " -ForegroundColor Blue
    Write-Host "                   Moving obsolete files to 'obsolete' folder                  " -ForegroundColor Blue
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Blue
}

# Create obsolete directory
function Create-ObsoleteDirectory {
    if (!(Test-Path "obsolete")) {
        New-Item -ItemType Directory -Name "obsolete" | Out-Null
        Write-Info "Created 'obsolete' directory"
    }
    else {
        Write-Info "'obsolete' directory already exists"
    }
}

# Move file to obsolete folder if it exists
function Move-IfExists {
    param(
        [string]$FilePath,
        [string]$Description
    )
    
    if (Test-Path $FilePath) {
        Move-Item $FilePath "obsolete\" -Force
        Write-Success "$FilePath → obsolete\ ($Description)"
        return $true
    }
    else {
        Write-Warning "$FilePath not found"
        return $false
    }
}

# Main cleanup function
function Main {
    Write-Header
    
    Write-Host "This script will move obsolete and debug files to an 'obsolete' folder." -ForegroundColor Cyan
    Write-Host "Files will be preserved for reference but removed from the main directory." -ForegroundColor Cyan
    Write-Host ""
    
    $continue = Read-Host "Continue with cleanup? (y/N)"
    if ($continue -notmatch "^[Yy]$") {
        Write-Info "Cleanup cancelled by user"
        return
    }
    
    # Create obsolete directory
    Create-ObsoleteDirectory
    
    Write-Info "Moving debug and test files..."
    
    # Debug files
    Move-IfExists "simple_debug.py" "Simple debug utility"
    Move-IfExists "debug_bazarr.py" "Bazarr debug script"
    Move-IfExists "debug_credentials.py" "Credential debug script"
    Move-IfExists "debug_bazarr_direct.py" "Direct Bazarr debug script"
    
    # Test files
    Move-IfExists "test_pagination.py" "Pagination test"
    Move-IfExists "test_database.py" "Database test"
    Move-IfExists "test_bazarr_api.py" "Bazarr API test"
    Move-IfExists "test_bazarr.py" "Bazarr test"
    Move-IfExists "test_credentials.py" "Credentials test"
    Move-IfExists "test_fixes.py" "Fixes test"
    Move-IfExists "test_slice.py" "Slice test"
    
    Write-Info "Moving obsolete/duplicate files..."
    
    # Obsolete files
    Move-IfExists "bazarr_integration.py" "Old Bazarr integration (replaced by bazarr.py)"
    Move-IfExists "ssh_tunnel_manager.py" "SSH tunnel manager (unused feature)"
    Move-IfExists "update_bazarr_url.py" "URL update utility (one-time use)"
    Move-IfExists "SETUP.md" "Old setup guide (replaced by README.md)"
    
    Write-Info "Moving backup and temporary database files..."
    
    # Backup files
    Move-IfExists "bazarr_sync_tracking.db.backup" "Database backup"
    Move-IfExists "subsync.db.backup" "Database backup"
    Move-IfExists "test_write.db" "Test database"
    
    # Count moved files
    $movedCount = 0
    if (Test-Path "obsolete") {
        $movedCount = (Get-ChildItem "obsolete" -File).Count
    }
    
    Write-Host ""
    Write-Header
    Write-Info "🎉 Cleanup completed!"
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Green
    Write-Host "• Files moved to 'obsolete' folder: $movedCount" -ForegroundColor Cyan
    Write-Host "• Main directory is now cleaner and more organized" -ForegroundColor Cyan
    Write-Host "• All files are preserved in 'obsolete' folder for reference" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Note: You can safely delete the 'obsolete' folder if you don't need these files" -ForegroundColor Yellow
    Write-Host ""
}

# Run main function
Main
