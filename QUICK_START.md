# 🚀 Quick Start Guide - Enhanced Subtitle Sync System

## ⚡ 30-Second Setup

### Windows Users:
1. **Download** all project files to a folder
2. **Right-click** on `install_subsync.ps1` → "Run with PowerShell" (as Administrator)
3. **Double-click** `run_subsync.bat` to start
4. **Configure** Bazarr and Plex in Settings menu

### macOS/Linux Users:
1. **Download** all project files to a folder
2. **Open Terminal** in that folder
3. **Run**: `chmod +x install_subsync.sh && ./install_subsync.sh`
4. **Start**: `./run_subsync_mac.sh` (or `./run_subsync_linux.sh`)
5. **Configure** Bazarr and Plex in Settings menu

## 🎯 First-Time Configuration (5 minutes)

### Step 1: Configure Bazarr
1. Go to **Settings** (Option 5)
2. Choose **Configure Bazarr credentials** (Option 1)
3. Enter your Bazarr URL: `http://your-server-ip:6767`
4. Enter your Bazarr API key (found in Bazarr Settings → General → Security)
5. Test connection (Option 2)

### Step 2: Configure Plex  
1. In Settings, choose **Configure Plex credentials** (Option 3)
2. Enter your Plex URL: `http://your-server-ip:32400`
3. Get token using username/password (Option 2)
4. Test connection (Option 4)

### Step 3: Set Path Mappings
1. In Settings, choose **Configure path mappings** (Option 5)
2. View current mappings (Option 2)
3. Edit if needed (Option 3) or create new environment (Option 4)

## 🎬 Start Syncing!

### Sync a Single Movie:
1. **Main Menu** → **Sync Movies from Bazarr** (Option 1)
2. **Search** for your movie or browse the list
3. **Select** the movie and confirm sync
4. **Watch** as the subtitle gets synced and automatically set as default in Plex!

### Sync TV Series:
1. **Main Menu** → **Sync TV Series from Bazarr** (Option 2)  
2. **Search** for your series
3. **Select** the series - it will sync all episodes automatically
4. **Plex integration** sets each synced episode subtitle as default

### Bulk Sync Everything:
1. **Main Menu** → **Bulk Sync ALL Media** (Option 3)
2. **Confirm** - this will process your entire library
3. **Go get coffee** ☕ - this can take hours for large libraries!

## 🔧 Common Settings

### Recommended Settings for Most Users:
- **Max workers**: 2 (can increase to 3-4 on powerful systems)
- **Sync timeout**: 300 seconds
- **Auto archive**: Yes (keeps your system tidy)
- **Plex integration**: Yes (automatically sets synced subtitles as default)

### Path Mapping Examples:

**Mac Setup:**
- Movies Local: `/Volumes/Data/Movies`
- Movies Plex: `/PlexMedia/Movies`
- Series Local: `/Volumes/Data/TVShows`
- Series Plex: `/PlexMedia/TVShows`

**Windows Setup:**
- Movies Local: `\\NAS\Movies` or `D:\Movies`
- Movies Plex: `/PlexMedia/Movies`
- Series Local: `\\NAS\TVShows` or `D:\TVShows`  
- Series Plex: `/PlexMedia/TVShows`

## 🎉 That's It!

Your system is now ready to automatically:
✅ Find out-of-sync subtitles in your Bazarr library  
✅ Sync them perfectly using advanced audio analysis  
✅ Set them as default subtitles in Plex automatically  
✅ Archive original files and keep your system organized  

## 🆘 Need Help?

- **Check README.md** for detailed documentation
- **Check logs/** folder for error messages  
- **Use Settings → Test connections** to verify setup
- **Run test scripts** to validate your installation

**Happy syncing!** 🎬✨
