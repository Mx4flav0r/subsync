# Subtitle Sync System - Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install ffsubsync requests
   ```

2. **Run the system:**
   ```bash
   python main.py
   ```

## Common Issues

### Archive Permission Errors

If you see permission denied errors when archiving files, run:

```bash
# Fix archive directory ownership
sudo chown -R $USER ~/subtitle_archive

# Or use the built-in permission fixer
python fix_permissions.py
```

### First-Time Setup

The system will automatically create:
- `~/subtitle_archive/` - Archive directory for processed files
- Database files for tracking sync history

### Troubleshooting

**Permission Denied Errors:**
```
❌ Permission denied archiving file: [Errno 13] Permission denied
```

**Solution:**
```bash
sudo chown -R $USER ~/subtitle_archive
chmod 755 ~/subtitle_archive
```

**Archive Directory Issues:**
If the archive directory was created with wrong permissions (e.g., by sudo), fix with:
```bash
sudo chown -R $(whoami) ~/subtitle_archive
```

## Configuration

Edit `config.py` to adjust:
- Archive settings (`auto_archive: True/False`)
- Sync parameters
- Path mappings

## Archive Functionality

When `auto_archive` is enabled:
- ✅ Creates `.synced.srt` files after successful sync
- ✅ Moves original `.srt` files to `~/subtitle_archive/originals/`
- ✅ Moves backup `.srt.backup` files to `~/subtitle_archive/backups/`
- ✅ Keeps only synced versions in the source directory

## Support

If you encounter issues:
1. Run `python fix_permissions.py` to check permissions
2. Check that ffsubsync is installed: `ffsubsync --version`
3. Verify Bazarr connection in the settings menu
