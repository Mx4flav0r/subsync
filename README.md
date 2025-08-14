# 🚀 Enhanced Subtitle Sync System

A powerful, intelligent subtitle synchronization system that automatically syncs subtitles with video files using advanced audio analysis. Integrates seamlessly with Bazarr and Plex for a complete media management solution.

## ✨ Features

- **🎯 Advanced Sync Engine**: Powered by ffsubsync with multiple VAD (Voice Activity Detection) methods
- **🌐 Bazarr Integration**: Automatic discovery and sync of movies and TV series from your Bazarr instance
- **🎬 Plex Integration**: Automatically sets synced subtitles as default in your Plex server
- **📦 Archive Management**: Intelligent file management with backup and restore capabilities
- **🔍 Duplicate Detection**: Smart skip logic to avoid re-processing already synced content
- **🗺️ Path Mapping**: Environment-aware path management for multi-device deployments
- **📊 Statistics & Tracking**: Comprehensive sync history and performance metrics
- **⚡ Parallel Processing**: Bulk operations with configurable worker threads
- **🎨 Beautiful CLI**: Intuitive menu-driven interface with colored output

## 🎯 What This System Does

The Enhanced Subtitle Sync System solves the common problem of out-of-sync subtitles by:

1. **Analyzing audio tracks** from your video files using advanced voice detection
2. **Comparing subtitle timing** with detected speech patterns
3. **Automatically adjusting** subtitle timing to perfectly match the audio
4. **Integrating with your media setup** (Bazarr for discovery, Plex for playback)
5. **Managing the entire process** from discovery to final playback configuration

## 📋 Requirements

### System Requirements
- **Python 3.8+** (Python 3.9+ recommended)
- **FFmpeg** (for audio processing)
- **2GB+ RAM** (4GB+ recommended for bulk operations)
- **Network access** to your Bazarr and Plex servers

### Supported Platforms
- ✅ **macOS** (Intel and Apple Silicon)
- ✅ **Linux** (Ubuntu, Debian, CentOS, Arch)
- ✅ **Windows** (Windows 10/11)

## 🚀 Quick Start

### Option 1: Automated Installation

#### macOS/Linux:
```bash
# Download the project files to your desired directory
# Make the install script executable
chmod +x install_subsync.sh

# Run the installation
./install_subsync.sh

# Start the system
./run_subsync_mac.sh     # macOS
./run_subsync_linux.sh   # Linux
```

#### Windows:
```powershell
# Open PowerShell as Administrator
# Navigate to the project directory
# Run the installation
.\install_subsync.ps1

# Start the system
.\run_subsync.bat
# OR
.\run_subsync.ps1
```

### Option 2: Manual Installation

1. **Install Python 3.8+**
2. **Install FFmpeg**
3. **Clone/Download project files**
4. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```
5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Run the system**:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### First-Time Setup

1. **Start the application**: `python main.py`
2. **Go to Settings** (Option 5)
3. **Configure Bazarr credentials** (Option 1)
4. **Configure Plex credentials** (Option 3) 
5. **Set up path mappings** (Option 5)

### Bazarr Configuration
- **URL**: Your Bazarr server URL (e.g., `http://192.168.1.100:6767`)
- **API Key**: Found in Bazarr Settings → General → Security

### Plex Configuration  
- **URL**: Your Plex server URL (e.g., `http://192.168.1.100:32400`)
- **Token**: Get via Settings → Configure Plex credentials → Get token using username/password

### Path Mapping Configuration
Configure how local file paths map to Plex paths for different environments:

**Example Configurations:**

| Environment | Local Path | Plex Path |
|-------------|------------|-----------|
| Mac M1 | `/Volumes/Data/Movies` | `/PlexMedia/Movies` |
| Windows | `\\\\NAS\\Movies` | `/PlexMedia/Movies` |
| Docker | `/data/movies` | `/PlexMedia/Movies` |

## 📖 Menu Walkthrough

### 🎯 Main Menu Options

#### 1. 🎬 Sync Movies from Bazarr
- **Purpose**: Discover and sync movie subtitles from your Bazarr instance
- **Process**: 
  1. Fetches movie list from Bazarr
  2. Displays movies with search/filter options
  3. Syncs selected movies using advanced audio analysis
  4. Automatically sets synced subtitles as default in Plex
- **When to use**: When you want to sync specific movies or browse your movie collection

#### 2. 📺 Sync TV Series from Bazarr  
- **Purpose**: Discover and sync TV series subtitles from your Bazarr instance
- **Process**:
  1. Fetches TV series list from Bazarr
  2. For each selected series, finds all episodes
  3. Syncs each episode that doesn't already have synced subtitles
  4. Updates Plex with synced subtitle preferences
- **When to use**: When you want to sync entire seasons or specific TV series

#### 3. 🚀 Bulk Sync ALL Media
- **Purpose**: Process all movies and series in one operation
- **Process**:
  1. Fetches complete media library from Bazarr
  2. Processes movies first, then TV series
  3. Uses parallel processing for faster completion
  4. Comprehensive progress reporting
- **When to use**: For initial setup or when you want to sync your entire library
- **⚠️ Warning**: Can take several hours for large libraries

#### 4. 📊 Statistics & Reports
- **Purpose**: View sync performance and history
- **Information shown**:
  - Total sync operations performed
  - Success/failure rates
  - Processing times and performance metrics
  - Recent sync activity
  - Archive statistics
- **When to use**: To monitor system performance and track sync history

#### 5. ⚙️ Settings & Configuration
Comprehensive configuration management:

##### 5.1 Configure Bazarr credentials
- Set Bazarr server URL and API key
- Test connection to ensure proper setup

##### 5.2 Test Bazarr connection  
- Verify connectivity and authentication
- Display server information and available media

##### 5.3 Configure Plex credentials
- Set Plex server URL
- Get authentication token (manual entry or automatic retrieval)

##### 5.4 Test Plex connection
- Verify connectivity and authentication  
- Display available libraries and server information

##### 5.5 Configure path mappings
- **Environment profiles**: Create configurations for different deployment environments
- **Path validation**: Test if configured paths are accessible
- **Environment switching**: Easy switching between Mac, Windows, Docker setups
- **Custom environments**: Create your own environment profiles

##### 5.6 Set preferred languages
- Configure which subtitle languages to prioritize
- Support for multiple language preferences

##### 5.7 Configure sync settings
- **Max workers**: Number of parallel sync operations (default: 2)
- **Sync timeout**: Maximum time per sync operation (default: 300s)
- **VAD method**: Voice Activity Detection method preference
- **Auto archive**: Enable/disable automatic file archiving
- **Plex integration**: Enable/disable automatic Plex subtitle configuration

##### 5.8 Show current configuration
- Display all current settings in a readable format
- Useful for troubleshooting and verification

##### 5.9 Reset to defaults
- Restore all settings to factory defaults
- ⚠️ Use with caution - will erase all custom configurations

#### 6. 📦 Archive Management
Intelligent file management system:

##### 6.1 Show archive statistics
- Total archived files and storage usage
- Archive age and cleanup recommendations

##### 6.2 View archived files
- Browse archived subtitle files
- Search and filter capabilities

##### 6.3 Restore files
- Restore archived files to their original locations
- Selective restoration options

##### 6.4 Clean old archives
- Remove old archived files to free up space
- Configurable age thresholds

#### 7. 🔧 System Tools
Advanced system utilities:

##### 7.1 Database maintenance
- Compact and optimize databases
- Clear old sync history

##### 7.2 Permission fixes
- Fix file permissions for subtitle files
- Resolve ownership issues (macOS/Linux)

##### 7.3 Path validation
- Test accessibility of all configured paths
- Network connectivity testing

#### 8. ❓ Help & Status
- System status overview
- Version information
- Quick help and troubleshooting tips
- Link to documentation

#### 9. 🚪 Exit
- Safely close the application
- Clean up temporary files

## 📁 File Structure & Descriptions

### Core Application Files

| File | Purpose | Description |
|------|---------|-------------|
| `main.py` | **Entry Point** | Main application launcher and coordinator |
| `cli.py` | **User Interface** | Command-line interface with all menus and user interactions |
| `sync_engine.py` | **Sync Orchestrator** | High-level sync coordination and business logic |
| `path_mapper.py` | **Core Sync Engine** | Low-level subtitle synchronization using ffsubsync |
| `config.py` | **Configuration Management** | Settings storage, validation, and environment handling |
| `database.py` | **Data Storage** | SQLite database operations for sync history and tracking |
| `bazarr.py` | **Bazarr Integration** | API client for Bazarr media server integration |
| `plex_client.py` | **Plex Integration** | API client for Plex media server integration |
| `archive_manager.py` | **File Management** | Intelligent archiving and restoration of subtitle files |
| `credential_manager.py` | **Security** | Secure storage and retrieval of API credentials |
| `path_utils.py` | **Path Management** | Environment-aware path mapping and conversion utilities |

### Utility Files

| File | Purpose | Description |
|------|---------|-------------|
| `get_plex_token.py` | **Plex Authentication** | Standalone utility to retrieve Plex authentication tokens |
| `database_manager.py` | **Database Admin** | Database schema management and migrations |
| `test_plex_integration.py` | **Testing** | Test script for Plex integration functionality |
| `test_path_mapping.py` | **Testing** | Test script for path mapping system |

### Installation & Launch Scripts

| File | Purpose | Platform |
|------|---------|----------|
| `install_subsync.sh` | **Automated Installation** | macOS/Linux |
| `install_subsync.ps1` | **Automated Installation** | Windows |
| `run_subsync_mac.sh` | **Launcher** | macOS |
| `run_subsync_linux.sh` | **Launcher** | Linux |
| `run_subsync.ps1` | **Launcher** | Windows PowerShell |
| `run_subsync.bat` | **Launcher** | Windows Batch |

### Configuration & Data Files

| File | Purpose | Description |
|------|---------|-------------|
| `subsync_config.json` | **Main Configuration** | User settings, paths, and preferences |
| `requirements.txt` | **Dependencies** | Python package requirements |
| `README.md` | **Documentation** | This comprehensive guide |
| `bazarr_sync_tracking.db` | **Database** | Sync history and statistics |
| `subtitle_sync_history.db` | **Database** | Detailed operation tracking |

### Directory Structure
```
subsync/
├── 📄 Core application files
├── 🔧 Utility scripts  
├── 📦 Installation scripts
├── ⚙️ Configuration files
├── 🗃️ Database files
├── 📁 logs/ (created at runtime)
├── 📁 temp/ (created at runtime)
├── 📁 archive/ (created at runtime)
└── 📁 backups/ (created at runtime)
```

## 🔧 Troubleshooting

### Common Issues

#### FFmpeg Not Found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian  
sudo apt install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

#### Python Module Import Errors
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Permission Errors (macOS/Linux)
```bash
# Fix permissions
chmod +x *.sh
sudo chown -R $USER:$USER .
```

#### Plex Connection Issues
- Verify Plex server is running and accessible
- Check firewall settings
- Ensure correct URL and token configuration
- Test with Plex web interface first

#### Bazarr Connection Issues  
- Verify Bazarr is running and accessible
- Check API key in Bazarr Settings → General → Security
- Test API key with curl or browser

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export SUBSYNC_DEBUG=1  # macOS/Linux
set SUBSYNC_DEBUG=1     # Windows
```

### Log Files
Check log files in the `logs/` directory:
- `subsync.log`: General application logs
- `sync_operations.log`: Detailed sync operation logs
- `error.log`: Error messages and stack traces

## 🤝 Support

### Getting Help
1. Check this README for common solutions
2. Review log files for specific error messages
3. Verify all dependencies are properly installed
4. Test individual components (Bazarr, Plex) separately

### System Requirements Check
Run the test scripts to verify your setup:
```bash
python test_plex_integration.py
python test_path_mapping.py
```

### Performance Optimization
- **Reduce max_workers** if system becomes unresponsive
- **Increase sync_timeout** for problematic files
- **Enable auto_archive** to manage disk space
- **Use SSD storage** for better performance

## 📊 Performance Guidelines

### Recommended Settings by System

| System Specs | Max Workers | Sync Timeout | Expected Performance |
|--------------|-------------|--------------|---------------------|
| 4GB RAM, HDD | 1 | 600s | 2-3 files/minute |
| 8GB RAM, SSD | 2 | 300s | 4-6 files/minute |
| 16GB+ RAM, SSD | 3-4 | 300s | 8-12 files/minute |

### Network Considerations
- **Local network**: Optimal performance
- **VPN/Remote**: Increase timeouts, reduce workers
- **Slow connections**: Consider local Bazarr/Plex instances

## 🔐 Security Considerations

### API Keys and Tokens
- Store credentials securely using the built-in credential manager
- Regularly rotate Plex tokens
- Use read-only Bazarr API keys when possible

### Network Security
- Use HTTPS for Plex connections when possible
- Consider VPN for remote access
- Firewall rules for service access

### File Permissions
- Run with minimal required permissions
- Archive manager handles permission fixes automatically
- Avoid running as root/administrator unless necessary

## 🎉 Advanced Usage

### Custom Environments
Create custom environment profiles for different deployment scenarios:
1. **Development Environment**: Local paths for testing
2. **Production Environment**: Network paths for production use
3. **Docker Environment**: Container-specific paths
4. **Multi-User Environment**: Shared network storage paths

### Automation
The system can be automated using cron jobs or scheduled tasks:
```bash
# Daily sync at 2 AM
0 2 * * * /path/to/subsync/run_subsync_linux.sh --bulk --quiet
```

### Integration with Other Tools
- **Sonarr/Radarr**: Use webhook notifications to trigger syncs
- **Tautulli**: Monitor Plex usage to prioritize sync operations
- **Grafana**: Create dashboards using sync statistics

---

## 📄 License

This project is provided as-is for personal and educational use. Please ensure compliance with all applicable laws and service terms when using with media content.

---

**🚀 Enhanced Subtitle Sync System** - Making your media perfectly synchronized, automatically! 🎬
