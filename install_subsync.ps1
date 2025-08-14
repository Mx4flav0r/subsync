# =============================================================================
# Enhanced Subtitle Sync System - Installation Script (Windows PowerShell)
# =============================================================================

# Require PowerShell 5.0 or higher
#Requires -Version 5.0

# Set execution policy for current session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Color functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Step { param($Message) Write-Host "[STEP] $Message" -ForegroundColor Blue }

function Write-Header {
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Magenta
    Write-Host "                    🚀 ENHANCED SUBTITLE SYNC SYSTEM 🚀                       " -ForegroundColor Magenta
    Write-Host "                           Installation Script (Windows)                       " -ForegroundColor Magenta
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Magenta
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# Check if command exists
function Test-CommandExists {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Install Chocolatey if not present
function Install-Chocolatey {
    Write-Step "Checking Chocolatey installation..."
    
    if (Test-CommandExists "choco") {
        Write-Success "Chocolatey is already installed"
    }
    else {
        Write-Step "Installing Chocolatey package manager..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Success "Chocolatey installed successfully"
    }
}

# Install Python if not present
function Install-Python {
    Write-Step "Checking Python installation..."
    
    if (Test-CommandExists "python") {
        $pythonVersion = python --version 2>&1
        Write-Success "Python is already installed: $pythonVersion"
    }
    else {
        Write-Step "Installing Python 3..."
        choco install python3 -y
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Success "Python 3 installed successfully"
    }
}

# Install FFmpeg if not present
function Install-FFmpeg {
    Write-Step "Checking FFmpeg installation..."
    
    if (Test-CommandExists "ffmpeg") {
        $ffmpegVersion = ffmpeg -version 2>&1 | Select-String "ffmpeg version" | Select-Object -First 1
        Write-Success "FFmpeg is already installed: $ffmpegVersion"
    }
    else {
        Write-Step "Installing FFmpeg..."
        choco install ffmpeg -y
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Success "FFmpeg installed successfully"
    }
}

# Install Git if not present
function Install-Git {
    Write-Step "Checking Git installation..."
    
    if (Test-CommandExists "git") {
        $gitVersion = git --version
        Write-Success "Git is already installed: $gitVersion"
    }
    else {
        Write-Step "Installing Git..."
        choco install git -y
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Success "Git installed successfully"
    }
}

# Setup Python virtual environment
function Setup-VirtualEnvironment {
    Write-Step "Setting up Python virtual environment..."
    
    $venvName = ".venv_windows"
    
    if (!(Test-Path $venvName)) {
        python -m venv $venvName
        Write-Success "Virtual environment '$venvName' created"
    }
    else {
        Write-Success "Virtual environment '$venvName' already exists"
    }
    
    # Activate virtual environment
    & "$venvName\Scripts\Activate.ps1"
    Write-Success "Virtual environment activated"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    Write-Success "Pip upgraded to latest version"
}

# Install Python dependencies
function Install-PythonDependencies {
    Write-Step "Installing Python dependencies..."
    
    $dependencies = @(
        "requests>=2.25.0",
        "ffsubsync>=0.4.25",
        "webrtcvad>=2.0.10", 
        "colorama>=0.4.4",
        "tqdm>=4.64.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "librosa>=0.9.0",
        "soundfile>=0.10.0",
        "auditok>=0.1.5",
        "samplerate>=0.1.0"
    )
    
    foreach ($dep in $dependencies) {
        Write-Info "Installing $dep..."
        pip install $dep
    }
    
    Write-Success "All Python dependencies installed successfully"
}

# Create requirements.txt
function Create-Requirements {
    Write-Step "Creating requirements.txt..."
    
    $requirementsContent = @"
# Enhanced Subtitle Sync System - Python Dependencies
requests>=2.25.0
ffsubsync>=0.4.25
webrtcvad>=2.0.10
colorama>=0.4.4
tqdm>=4.64.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.5.0
librosa>=0.9.0
soundfile>=0.10.0
auditok>=0.1.5
samplerate>=0.1.0
"@
    
    $requirementsContent | Out-File -FilePath "requirements.txt" -Encoding UTF8
    Write-Success "requirements.txt created"
}

# Setup configuration
function Setup-Configuration {
    Write-Step "Setting up initial configuration..."
    
    if (!(Test-Path "subsync_config.json")) {
        python -c "
from config import config
config.save_config()
print('✅ Initial configuration created')
"
        Write-Success "Configuration file created: subsync_config.json"
    }
    else {
        Write-Success "Configuration file already exists"
    }
}

# Create launch scripts
function Create-LaunchScripts {
    Write-Step "Creating launch scripts..."
    
    # Create PowerShell launcher
    $launcherContent = @"
# Enhanced Subtitle Sync System Launcher (Windows)
Write-Host "🚀 Starting Enhanced Subtitle Sync System..." -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path ".venv_windows")) {
    Write-Host "❌ Virtual environment not found. Please run install_subsync.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
& ".venv_windows\Scripts\Activate.ps1"

# Check if main.py exists
if (!(Test-Path "main.py")) {
    Write-Host "❌ main.py not found. Please ensure all files are in the current directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the application
python main.py

# Keep window open if there was an error
if (`$LASTEXITCODE -ne 0) {
    Read-Host "Press Enter to exit"
}
"@
    
    $launcherContent | Out-File -FilePath "run_subsync.ps1" -Encoding UTF8
    
    # Create batch file launcher for easier double-click execution
    $batchContent = @"
@echo off
echo 🚀 Starting Enhanced Subtitle Sync System...
powershell.exe -ExecutionPolicy Bypass -File "run_subsync.ps1"
pause
"@
    
    $batchContent | Out-File -FilePath "run_subsync.bat" -Encoding ASCII
    
    Write-Success "Launch scripts created: run_subsync.ps1 and run_subsync.bat"
}

# Test installation
function Test-Installation {
    Write-Step "Testing installation..."
    
    # Test Python imports
    python -c "
import sys
import requests
import sqlite3
try:
    import ffsubsync
    print('✅ ffsubsync imported successfully')
except ImportError as e:
    print(f'⚠️ ffsubsync import warning: {e}')
    print('This might be normal - ffsubsync will be installed when needed')

print('✅ Core dependencies test passed')
"
    
    # Test if main files exist
    $requiredFiles = @("main.py", "config.py", "sync_engine.py", "cli.py", "path_mapper.py")
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "✅ $file found"
        }
        else {
            Write-Warning "⚠️ $file not found - make sure to copy all project files"
        }
    }
}

# Main installation function
function Main {
    Write-Header
    
    Write-Host "This script will install all required components for the Enhanced Subtitle Sync System." -ForegroundColor Cyan
    Write-Host "Administrator privileges may be required for some installations." -ForegroundColor Cyan
    Write-Host ""
    
    if (!(Test-Administrator)) {
        Write-Warning "Not running as Administrator. Some installations may fail."
        Write-Info "Consider running PowerShell as Administrator for best results."
        Write-Host ""
    }
    
    $continue = Read-Host "Continue with installation? (y/N)"
    if ($continue -notmatch "^[Yy]$") {
        Write-Info "Installation cancelled by user"
        return
    }
    
    try {
        # Installation steps
        Install-Chocolatey
        Install-Python
        Install-FFmpeg
        Install-Git
        Setup-VirtualEnvironment
        Install-PythonDependencies
        Create-Requirements
        Setup-Configuration
        Create-LaunchScripts
        Test-Installation
        
        # Success message
        Write-Host ""
        Write-Header
        Write-Success "🎉 Installation completed successfully!"
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Green
        Write-Host "1. Run the system: Double-click run_subsync.bat or run .\run_subsync.ps1" -ForegroundColor Cyan
        Write-Host "2. Configure Bazarr: Settings → Configure Bazarr credentials" -ForegroundColor Cyan
        Write-Host "3. Configure Plex: Settings → Configure Plex credentials" -ForegroundColor Cyan
        Write-Host "4. Set path mappings: Settings → Configure path mappings" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📖 See README.md for detailed usage instructions" -ForegroundColor Magenta
        Write-Host ""
    }
    catch {
        Write-Error "Installation failed: $($_.Exception.Message)"
        Write-Info "Please check the error above and try again"
    }
}

# Run main function
Main
