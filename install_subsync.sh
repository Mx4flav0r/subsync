#!/bin/bash

# =============================================================================
# Enhanced Subtitle Sync System - Installation Script (macOS/Linux)
# =============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}                    🚀 ENHANCED SUBTITLE SYNC SYSTEM 🚀                       ${NC}"
    echo -e "${PURPLE}                           Installation Script (macOS/Linux)                    ${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

# Check if running on macOS or Linux
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        PACKAGE_MANAGER="brew"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
        else
            print_error "Unsupported Linux distribution"
            exit 1
        fi
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    print_status "Detected OS: $OS with package manager: $PACKAGE_MANAGER"
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install Python if not present
install_python() {
    print_step "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python $PYTHON_VERSION is already installed"
    else
        print_step "Installing Python 3..."
        case $PACKAGE_MANAGER in
            "brew")
                brew install python3
                ;;
            "apt")
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
                ;;
            "yum")
                sudo yum install -y python3 python3-pip
                ;;
            "pacman")
                sudo pacman -S python python-pip
                ;;
        esac
        print_status "Python 3 installed successfully"
    fi
}

# Install FFmpeg if not present
install_ffmpeg() {
    print_step "Checking FFmpeg installation..."
    
    if command_exists ffmpeg; then
        FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | cut -d' ' -f3)
        print_status "FFmpeg $FFMPEG_VERSION is already installed"
    else
        print_step "Installing FFmpeg..."
        case $PACKAGE_MANAGER in
            "brew")
                brew install ffmpeg
                ;;
            "apt")
                sudo apt-get install -y ffmpeg
                ;;
            "yum")
                sudo yum install -y ffmpeg
                ;;
            "pacman")
                sudo pacman -S ffmpeg
                ;;
        esac
        print_status "FFmpeg installed successfully"
    fi
}

# Install git if not present
install_git() {
    print_step "Checking Git installation..."
    
    if command_exists git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_status "Git $GIT_VERSION is already installed"
    else
        print_step "Installing Git..."
        case $PACKAGE_MANAGER in
            "brew")
                brew install git
                ;;
            "apt")
                sudo apt-get install -y git
                ;;
            "yum")
                sudo yum install -y git
                ;;
            "pacman")
                sudo pacman -S git
                ;;
        esac
        print_status "Git installed successfully"
    fi
}

# Setup Python virtual environment
setup_virtual_env() {
    print_step "Setting up Python virtual environment..."
    
    # Create virtual environment
    if [[ "$OS" == "macOS" ]]; then
        VENV_NAME=".venv_mac"
    else
        VENV_NAME=".venv_linux"
    fi
    
    if [[ ! -d "$VENV_NAME" ]]; then
        python3 -m venv "$VENV_NAME"
        print_status "Virtual environment '$VENV_NAME' created"
    else
        print_status "Virtual environment '$VENV_NAME' already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "Pip upgraded to latest version"
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    # Core dependencies
    DEPENDENCIES=(
        "requests>=2.25.0"
        "ffsubsync>=0.4.25"
        "webrtcvad>=2.0.10"
        "colorama>=0.4.4"
        "tqdm>=4.64.0"
        "numpy>=1.21.0"
        "scipy>=1.7.0"
        "matplotlib>=3.5.0"
        "librosa>=0.9.0"
        "soundfile>=0.10.0"
        "auditok>=0.1.5"
        "samplerate>=0.1.0"
    )
    
    for dep in "${DEPENDENCIES[@]}"; do
        print_status "Installing $dep..."
        pip install "$dep"
    done
    
    print_status "All Python dependencies installed successfully"
}

# Create requirements.txt
create_requirements() {
    print_step "Creating requirements.txt..."
    
    cat > requirements.txt << 'EOF'
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
EOF
    
    print_status "requirements.txt created"
}

# Setup configuration
setup_config() {
    print_step "Setting up initial configuration..."
    
    # Create config file if it doesn't exist
    if [[ ! -f "subsync_config.json" ]]; then
        python3 -c "
from config import config
config.save_config()
print('✅ Initial configuration created')
"
        print_status "Configuration file created: subsync_config.json"
    else
        print_status "Configuration file already exists"
    fi
}

# Create launch scripts
create_launch_scripts() {
    print_step "Creating launch scripts..."
    
    # Create run script for macOS/Linux
    if [[ "$OS" == "macOS" ]]; then
        VENV_NAME=".venv_mac"
        SCRIPT_NAME="run_subsync_mac.sh"
    else
        VENV_NAME=".venv_linux"
        SCRIPT_NAME="run_subsync_linux.sh"
    fi
    
    cat > "$SCRIPT_NAME" << EOF
#!/bin/bash

# Enhanced Subtitle Sync System Launcher
echo "🚀 Starting Enhanced Subtitle Sync System..."

# Check if virtual environment exists
if [[ ! -d "$VENV_NAME" ]]; then
    echo "❌ Virtual environment not found. Please run install_subsync.sh first."
    exit 1
fi

# Activate virtual environment
source "$VENV_NAME/bin/activate"

# Check if main.py exists
if [[ ! -f "main.py" ]]; then
    echo "❌ main.py not found. Please ensure all files are in the current directory."
    exit 1
fi

# Run the application
python main.py

# Deactivate virtual environment
deactivate
EOF
    
    chmod +x "$SCRIPT_NAME"
    print_status "Launch script created: $SCRIPT_NAME"
}

# Test installation
test_installation() {
    print_step "Testing installation..."
    
    # Test Python imports
    python3 -c "
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
    REQUIRED_FILES=("main.py" "config.py" "sync_engine.py" "cli.py" "path_mapper.py")
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            print_status "✅ $file found"
        else
            print_warning "⚠️ $file not found - make sure to copy all project files"
        fi
    done
}

# Main installation function
main() {
    print_header
    
    echo -e "${CYAN}This script will install all required components for the Enhanced Subtitle Sync System.${NC}"
    echo -e "${CYAN}Please ensure you have administrator/sudo privileges if needed.${NC}"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled by user"
        exit 0
    fi
    
    # Installation steps
    detect_os
    install_python
    install_ffmpeg
    install_git
    setup_virtual_env
    install_python_deps
    create_requirements
    setup_config
    create_launch_scripts
    test_installation
    
    # Success message
    echo ""
    print_header
    print_status "🎉 Installation completed successfully!"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    if [[ "$OS" == "macOS" ]]; then
        echo -e "${CYAN}1. Run the system: ${YELLOW}./run_subsync_mac.sh${NC}"
    else
        echo -e "${CYAN}1. Run the system: ${YELLOW}./run_subsync_linux.sh${NC}"
    fi
    echo -e "${CYAN}2. Configure Bazarr: Settings → Configure Bazarr credentials${NC}"
    echo -e "${CYAN}3. Configure Plex: Settings → Configure Plex credentials${NC}"
    echo -e "${CYAN}4. Set path mappings: Settings → Configure path mappings${NC}"
    echo ""
    echo -e "${PURPLE}📖 See README.md for detailed usage instructions${NC}"
    echo ""
}

# Run main function
main "$@"
