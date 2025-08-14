# 📚 API Documentation - Subtitle Translation System

## Overview

This document provides comprehensive API documentation for the new subtitle translation features added to the Enhanced Subtitle Sync System.

## 🔌 BazarrIntegration Class

### New Methods

#### `get_wanted_movies() -> List[Dict]`

**Purpose**: Fetch movies that need subtitles from Bazarr's wanted list

**API Endpoint**: `/api/movies/wanted`

**Returns**: 
- `List[Dict]`: List of movie dictionaries
- Empty list if no movies need subtitles or on error

**Movie Data Structure**:
```python
{
    'title': str,           # Movie title
    'year': int,            # Release year  
    'path': str,            # Plex/Sonarr path
    'monitored': bool,      # Whether movie is monitored
    'profileId': int,       # Quality profile ID
    'radarrId': int,        # Radarr movie ID
    # ... additional Radarr metadata
}
```

**Example**:
```python
bazarr = BazarrIntegration(credential_manager)
wanted_movies = bazarr.get_wanted_movies()
print(f"Found {len(wanted_movies)} movies needing subtitles")
```

---

#### `get_wanted_series() -> List[Dict]`

**Purpose**: Fetch TV episodes that need subtitles from Bazarr's wanted list

**API Endpoint**: `/api/episodes/wanted`

**Returns**:
- `List[Dict]`: List of episode dictionaries
- Empty list if no episodes need subtitles or on error

**Episode Data Structure**:
```python
{
    'seriesTitle': str,      # Series name (e.g., "Animal Kingdom (2016)")
    'episodeTitle': str,     # Episode title  
    'episode_number': str,   # Format "SxE" (e.g., "5x2")
    'season': int,           # Season number
    'episode': int,          # Episode number
    'sonarrSeriesId': int,   # Sonarr series ID
    'sonarrEpisodeId': int,  # Sonarr episode ID
    'monitored': bool,       # Whether episode is monitored
    # ... additional Sonarr metadata
}
```

**Example**:
```python
wanted_episodes = bazarr.get_wanted_series()
for episode in wanted_episodes:
    print(f"{episode['seriesTitle']} {episode['episode_number']} - {episode['episodeTitle']}")
```

---

#### `get_all_wanted_items() -> Dict[str, Any]`

**Purpose**: Get combined results from both movies and TV episodes

**Returns**:
```python
{
    'movies': List[Dict],    # Results from get_wanted_movies()
    'series': List[Dict],    # Results from get_wanted_series()  
    'total': int            # Total count of items needing subtitles
}
```

**Example**:
```python
all_wanted = bazarr.get_all_wanted_items()
print(f"Total items needing subtitles: {all_wanted['total']}")
print(f"Movies: {len(all_wanted['movies'])}")
print(f"TV Episodes: {len(all_wanted['series'])}")
```

---

## 🔧 SyncEngine Class

### New Methods

#### `process_wanted_items_with_translation(language: str = "nl") -> Dict[str, int]`

**Purpose**: Main orchestration method for processing wanted items with automatic translation

**Parameters**:
- `language` (str): Target language code (default: "nl" for Dutch)

**Returns**:
```python
{
    'successful': int,    # Items processed successfully
    'failed': int,        # Items that failed processing
    'skipped': int,       # Items that were skipped
    'translated': int     # Items where new subtitles were created via translation
}
```

**Prerequisites**:
- PathMapper must be available (`self.use_pathmapper = True`)
- Auto-translation must be enabled in config
- Bazarr integration must be functional

**Process Flow**:
1. Validates prerequisites (PathMapper, config, Bazarr)
2. Fetches wanted items using `bazarr_client.get_all_wanted_items()`
3. Processes movies using `_find_movie_path()` and `_process_wanted_item_translation()`
4. Processes TV episodes using `_find_episode_path()` and `_process_wanted_item_translation()`
5. Returns comprehensive results with translation counts

**Example**:
```python
sync_engine = SyncEngine()
results = sync_engine.process_wanted_items_with_translation()
print(f"Successfully translated: {results['translated']} subtitle files")
```

---

#### `_find_movie_path(movie_data: dict) -> str`

**Purpose**: Find local file path for a movie from Bazarr data

**Parameters**:
- `movie_data` (dict): Movie data from Bazarr API

**Returns**:
- `str`: Full path to movie file if found
- `None`: If movie file cannot be located

**Search Strategy**:
1. **Direct Path Mapping**: Convert Bazarr/Plex path to local path using path mappings
2. **Fuzzy Title Search**: Search all movie directories for matching titles

**Supported Movie Libraries**:
- `/Volumes/Data/Movies`
- `/Volumes/Data/Cartoons`
- `/Volumes/Data/Documentaries`
- `/Volumes/Data/Christmas`
- `/Volumes/Data/Dive`

**Example**:
```python
movie_data = {'title': '1917', 'path': '/PlexMedia/Movies/1917/1917.mkv'}
movie_path = sync_engine._find_movie_path(movie_data)
print(f"Found movie at: {movie_path}")
```

---

#### `_find_episode_path(episode_data: dict) -> str`

**Purpose**: Find local file path for a TV episode from Bazarr data

**Parameters**:
- `episode_data` (dict): Episode data from Bazarr API

**Returns**:
- `str`: Full path to episode file if found
- `None`: If episode file cannot be located

**Search Strategy**:
1. Extract series title from `episode_data['seriesTitle']`
2. Search `/Volumes/Data/TVShows` for matching series directory
3. Return first video file found (TODO: exact episode matching)

**TODO Enhancement**: Use `episode_number` field for exact episode matching

**Example**:
```python
episode_data = {
    'seriesTitle': 'Animal Kingdom (2016)',
    'episode_number': '5x2',
    'episodeTitle': 'What Remains'
}
episode_path = sync_engine._find_episode_path(episode_data)
```

---

#### `_process_wanted_item_translation(video_path: str, target_language: str) -> str`

**Purpose**: Process a single item for subtitle translation

**Parameters**:
- `video_path` (str): Full path to video file
- `target_language` (str): Target language code (e.g., "nl")

**Returns**:
- `str`: Path to subtitle file (existing or newly created)
- `None`: If translation failed

**Process**:
1. Check if target language subtitles already exist
2. If not, use `SubtitleTranslator.find_and_translate_subtitles()`
3. Return path to subtitle file if successful

**Example**:
```python
video_path = "/Volumes/Data/Movies/1917/1917.mkv"
subtitle_path = sync_engine._process_wanted_item_translation(video_path, "nl")
if subtitle_path:
    print(f"Dutch subtitles available: {subtitle_path}")
```

---

## 🌐 SubtitleTranslator Class

### Main Methods

#### `find_and_translate_subtitles(video_path: str, target_language: str = 'nl') -> Optional[str]`

**Purpose**: Main entry point for subtitle translation

**Parameters**:
- `video_path` (str): Full path to video file
- `target_language` (str): Target language code (default: 'nl')

**Returns**:
- `str`: Path to successfully created translated subtitle file
- `None`: If no suitable source subtitles found or translation failed

**Workflow**:
1. **Discovery**: Search for existing subtitle files using `_find_existing_subtitles()`
2. **Extraction**: If no external files, extract embedded subtitles using `_extract_embedded_subtitles()`
3. **Selection**: Choose best source subtitle using `_select_best_subtitle()`
4. **Translation**: Translate subtitle file using `_translate_subtitle_file()`

**Example**:
```python
translator = SubtitleTranslator()
result = translator.find_and_translate_subtitles('/path/to/movie.mkv', 'nl')
if result:
    print(f"Dutch subtitles created: {result}")
```

---

#### `_find_existing_subtitles(video_path: str) -> List[Tuple[str, str]]`

**Purpose**: Find existing subtitle files next to video

**Returns**: List of tuples `(subtitle_path, detected_language)`

**Supported Formats**: `.srt`, `.vtt`, `.ass`, `.ssa`, `.sub`

---

#### `_extract_embedded_subtitles(video_path: str) -> List[Tuple[str, str]]`

**Purpose**: Extract embedded subtitles using ffmpeg

**Dependencies**: Requires `ffmpeg` and `ffprobe` in system PATH

**Returns**: List of tuples `(extracted_file_path, language)`

**Process**:
1. Use `ffprobe` to detect subtitle streams
2. Extract each stream to `.srt` format using `ffmpeg`
3. Skip streams already in target language

---

#### `_translate_subtitle_file(subtitle_path: str, target_language: str) -> Optional[str]`

**Purpose**: Translate a subtitle file to target language

**Process**:
1. **Parse**: Read and parse subtitle content using `_parse_srt_content()`
2. **Translate**: Translate entries in batches using `_translate_subtitle_entries()`
3. **Generate**: Create output file using `_write_srt_file()`

**Output Format**: `{original_base}.{target_language}.translated.srt`

---

### Translation APIs

#### `_translate_libre(texts: List[str], target_language: str) -> List[str]`

**Service**: LibreTranslate (https://libretranslate.de)
**Status**: Free, rate-limited
**Quality**: Good for most content

#### `_translate_mymemory(texts: List[str], target_language: str) -> List[str]`

**Service**: MyMemory API (https://api.mymemory.translated.net)
**Status**: Free tier (1000 words/day)
**Quality**: Variable, good for simple content

#### `_translate_google(texts: List[str], target_language: str) -> List[str]`

**Service**: Google Translate API
**Status**: Requires API key (currently disabled)
**Quality**: Excellent

---

## 🎨 CLI Integration

### New Menu Methods

#### `_wanted_items_menu()`

**Purpose**: Display wanted items processing menu with options

**Features**:
- Preview of items needing subtitles
- Sample movie and episode display
- Processing options (all, movies only, TV only, preview only)
- Prerequisite validation

#### `_process_all_wanted_items()`

**Purpose**: Execute complete wanted items processing workflow

**Process**:
1. User confirmation
2. Call `sync_engine.process_wanted_items_with_translation()`
3. Display results with translation counts

#### `_preview_wanted_items(wanted_data: dict)`

**Purpose**: Display comprehensive preview without processing

**Display Format**:
- Up to 10 movies with titles and years
- Up to 10 TV episodes with series, season/episode, and titles
- Total counts with continuation indicators

---

## 🔧 Configuration

### Required Settings

```python
{
    "auto_translation": True,                           # Enable translation feature
    "translation_target_language": "nl",               # Target language
    "translation_source_priority": ["en", "es", "fr", "de"],  # Source language priority
    "cleanup_extracted_subtitles": True,               # Clean up temp files
    "path_mappings": {                                  # Path mapping for multiple libraries
        "/PlexMedia/Movies": "/Volumes/Data/Movies",
        "/PlexMedia/Cartoons": "/Volumes/Data/Cartoons",
        "/PlexMedia/Documentaries": "/Volumes/Data/Documentaries",
        "/PlexMedia/Christmas": "/Volumes/Data/Christmas",
        "/PlexMedia/Dive": "/Volumes/Data/Dive",
        "/PlexMedia/TVShows": "/Volumes/Data/TVShows"
    }
}
```

---

## 🚨 Error Handling

### Common Exceptions

- **`ConnectionError`**: Bazarr API unavailable
- **`TimeoutError`**: Translation API timeout
- **`FileNotFoundError`**: Video or subtitle files missing
- **`PermissionError`**: Cannot write subtitle files
- **`JSONDecodeError`**: Malformed API responses

### Error Recovery

- **API Fallback**: Automatic retry with alternative translation APIs
- **Graceful Degradation**: Continue processing other items if one fails
- **Detailed Logging**: Comprehensive error messages for debugging

---

## 📊 Performance Characteristics

### Processing Speed
- **Translation**: ~30-60 seconds per subtitle file
- **Discovery**: ~1-2 seconds per item
- **Batch Processing**: Linear scaling with item count

### Memory Usage
- **Base System**: ~50MB
- **Per Subtitle**: ~5-10MB during processing
- **Peak Usage**: Depends on subtitle file size

### API Rate Limits
- **LibreTranslate**: ~60 requests/minute
- **MyMemory**: 1000 words/day free tier
- **Recommended**: Process items in small batches

---

This comprehensive API documentation provides detailed information for developers working with or extending the subtitle translation system.
