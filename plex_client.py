#!/usr/bin/env python3
"""
Plex API Client for subtitle management
"""

import requests
import json
import os
from urllib.parse import quote
import xml.etree.ElementTree as ET

class PlexSubtitleManager:
    def __init__(self, plex_url, plex_token):
        """Initialize Plex client"""
        self.plex_url = plex_url.rstrip('/')
        self.plex_token = plex_token
        self.session = requests.Session()
        
        # Headers for all requests
        self.headers = {
            'X-Plex-Token': self.plex_token,
            'Accept': 'application/json',
            'X-Plex-Client-Identifier': 'SubSync-Manager',
            'X-Plex-Product': 'SubSync Manager',
            'X-Plex-Version': '1.0'
        }
        
        print(f"🎬 Plex client initialized: {plex_url}")
    
    def test_connection(self):
        """Test Plex server connection"""
        try:
            print(f"🧪 Testing connection to: {self.plex_url}")
            
            response = self.session.get(
                f"{self.plex_url}/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Plex server connection successful")
                
                try:
                    # Parse XML response
                    root = ET.fromstring(response.content)
                    server_name = root.get('friendlyName', 'Unknown')
                    version = root.get('version', 'Unknown')
                    
                    print(f"🎬 Server: {server_name}")
                    print(f"📱 Version: {version}")
                    return True
                    
                except ET.ParseError as e:
                    print(f"⚠️ XML parsing error: {e}")
                    print(f"🔍 Response content: {response.text[:200]}...")
                    
                    # If XML parsing fails but connection succeeded, still return True
                    if "MediaContainer" in response.text or "friendlyName" in response.text:
                        print("✅ Plex server detected despite XML parsing issue")
                        return True
                    else:
                        return False
                        
            else:
                print(f"❌ Plex connection failed: {response.status_code}")
                print(f"🔍 Response: {response.text[:200]}...")
                return False
                
        except requests.exceptions.ConnectTimeout:
            print(f"❌ Connection timeout - check if Plex server is running")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error - check server URL and network")
            return False
        except Exception as e:
            print(f"❌ Plex connection error: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            return False
    
    def get_libraries(self):
        """Get all Plex libraries"""
        try:
            response = self.session.get(
                f"{self.plex_url}/library/sections",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                libraries = []
                
                for directory in data.get('MediaContainer', {}).get('Directory', []):
                    libraries.append({
                        'key': directory.get('key'),
                        'title': directory.get('title'),
                        'type': directory.get('type'),
                        'location': directory.get('Location', [{}])[0].get('path', '') if directory.get('Location') else ''
                    })
                
                return libraries
            else:
                print(f"❌ Failed to get libraries: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting libraries: {e}")
            return []
    
    def search_media_by_path(self, video_path, series_title=None):
        """Search for media item by file path, with optional series title for better TV show matching"""
        try:
            # Get all libraries (both TV shows and movies)
            libraries = self.get_libraries()
            searchable_libraries = [lib for lib in libraries if lib['type'] in ['show', 'movie']]
            
            filename = os.path.basename(video_path)
            print(f"🔍 Searching for media: {filename}")
            if series_title:
                print(f"📺 Series context: {series_title}")
            print(f"📚 Found {len(searchable_libraries)} libraries to search")
            
            # If we have series title, prioritize TV show libraries
            tv_libraries = [lib for lib in searchable_libraries if lib['type'] == 'show']
            movie_libraries = [lib for lib in searchable_libraries if lib['type'] == 'movie']
            
            # Show which movie libraries we found
            if movie_libraries:
                movie_lib_names = [lib['title'] for lib in movie_libraries]
                print(f"🎬 Movie libraries found: {', '.join(movie_lib_names)}")
            
            # Search order: TV shows first if series_title provided, then movies
            search_order = tv_libraries + movie_libraries if series_title else searchable_libraries
            
            for library in search_order:
                print(f"   📁 Searching in: {library['title']} ({library['type']})")
                
                # Use different search strategies based on content type and available info
                if library['type'] == 'show' and series_title:
                    # TV Show: Search by series title first, then by filename
                    media_items = self._search_tv_show(library['key'], video_path, series_title)
                else:
                    # Movie or fallback: Search by filename
                    media_items = self._search_library_by_filename(library['key'], video_path)
                
                if media_items:
                    print(f"   ✅ Found {len(media_items)} matches")
                    return media_items[0]  # Return first match
            
            print("❌ No media found in Plex")
            return None
            
        except Exception as e:
            print(f"❌ Error searching media: {e}")
            return None
    
    def _search_tv_show(self, library_key, video_path, series_title):
        """Search for TV show episode by series title and episode info"""
        try:
            filename = os.path.basename(video_path)
            print(f"   🔍 TV Show search: '{series_title}' for file '{filename}'")
            
            # Extract episode information from filename
            import re
            season_episode_match = re.search(r'[Ss](\d+)[Ee](\d+)', filename)
            season_num = None
            episode_num = None
            
            if season_episode_match:
                season_num = int(season_episode_match.group(1))
                episode_num = int(season_episode_match.group(2))
                print(f"   📺 Detected: Season {season_num}, Episode {episode_num}")
            
            # First, find the show by title
            response = self.session.get(
                f"{self.plex_url}/library/sections/{library_key}/all",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"   ❌ Library query failed: {response.status_code}")
                return []
            
            data = response.json()
            show_matches = []
            
            # Find shows that match the series title
            for item in data.get('MediaContainer', {}).get('Metadata', []):
                if item.get('type') == 'show':
                    item_title = item.get('title', '')
                    if self._fuzzy_title_match(item_title.lower(), series_title.lower()):
                        show_matches.append(item)
                        print(f"   ✅ Found show match: '{item_title}' (Rating Key: {item.get('ratingKey')})")
            
            if not show_matches:
                print(f"   ❌ No show found matching '{series_title}'")
                return self._search_library_by_filename(library_key, video_path)  # Fallback
            
            # Search episodes in matching shows
            episode_matches = []
            
            for show in show_matches:
                show_key = show.get('ratingKey')
                
                # Get all episodes for this show
                episodes_response = self.session.get(
                    f"{self.plex_url}/library/metadata/{show_key}/allLeaves",
                    headers=self.headers
                )
                
                if episodes_response.status_code == 200:
                    episodes_data = episodes_response.json()
                    
                    for episode in episodes_data.get('MediaContainer', {}).get('Metadata', []):
                        # Try to match by season/episode number first
                        if (season_num is not None and episode_num is not None and
                            episode.get('parentIndex') == season_num and 
                            episode.get('index') == episode_num):
                            
                            # Found exact season/episode match
                            for media in episode.get('Media', []):
                                for part in media.get('Part', []):
                                    episode_matches.append({
                                        'rating_key': episode.get('ratingKey'),
                                        'title': f"{show.get('title')} - {episode.get('title', 'Episode')}",
                                        'file_path': part.get('file', ''),
                                        'media_id': media.get('id'),
                                        'part_id': part.get('id')
                                    })
                                    print(f"   ✅ Episode match: S{season_num:02d}E{episode_num:02d} - {episode.get('title', 'Unknown')}")
                        
                        # Also try filename matching as backup
                        for media in episode.get('Media', []):
                            for part in media.get('Part', []):
                                part_file = part.get('file', '')
                                if part_file and os.path.basename(part_file) == filename:
                                    episode_matches.append({
                                        'rating_key': episode.get('ratingKey'),
                                        'title': f"{show.get('title')} - {episode.get('title', 'Episode')}",
                                        'file_path': part_file,
                                        'media_id': media.get('id'),
                                        'part_id': part.get('id')
                                    })
                                    print(f"   ✅ Filename match: {os.path.basename(part_file)}")
            
            return episode_matches
            
        except Exception as e:
            print(f"❌ Error in TV show search: {e}")
            return []

    def _search_library_by_filename(self, library_key, video_path):
        """Search library for matching filename"""
        try:
            filename = os.path.basename(video_path)
            
            # Remove extension for search
            search_name = os.path.splitext(filename)[0]
            
            # Try direct filename search first
            matches = self._search_library_by_term(library_key, search_name)
            if matches:
                return matches
            
            # For movies, try extracting title from filename pattern
            # Common patterns: "Movie Title (Year)" or "Movie.Title.Year.Quality.etc"
            if any(year in search_name for year in ['2019', '2020', '2021', '2022', '2023', '2024']):
                # Try to extract clean title
                import re
                
                # Pattern 1: "Title (Year)" or "Title.Year"
                year_match = re.search(r'(.+?)[\.\s]*[\(\.]?(\d{4})[\)\.]?', search_name)
                if year_match:
                    clean_title = year_match.group(1).replace('.', ' ').replace('_', ' ').strip()
                    
                    # Try multiple title variations
                    title_variations = [
                        clean_title,
                        clean_title.replace(' s ', "'s "),  # "Dogs" -> "Dog's"
                        clean_title.replace('s ', "'s "),   # Handle "Dogs Journey" -> "Dog's Journey"
                    ]
                    
                    # Also try with common apostrophe patterns
                    if 's ' in clean_title:
                        # Convert "A Dogs Journey" to "A Dog's Journey"
                        apostrophe_title = re.sub(r'(\w)s\s+(\w)', r"\1's \2", clean_title)
                        title_variations.append(apostrophe_title)
                    
                    for title_var in title_variations:
                        print(f"   🎬 Trying title search: '{title_var}'")
                        matches = self._search_library_by_term(library_key, title_var)
                        if matches:
                            return matches
            
            return []
            
        except Exception as e:
            print(f"❌ Error searching library: {e}")
            return []
    
    def _search_library_by_term(self, library_key, search_term):
        """Search library by a specific term"""
        try:
            # First try exact title search
            response = self.session.get(
                f"{self.plex_url}/library/sections/{library_key}/all",
                headers=self.headers,
                params={'title': search_term}
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                
                # Look through all items
                for item in data.get('MediaContainer', {}).get('Metadata', []):
                    item_title = item.get('title', '').lower()
                    search_lower = search_term.lower()
                    
                    # Check for exact or partial matches
                    if (search_lower in item_title or 
                        item_title in search_lower or
                        self._fuzzy_title_match(item_title, search_lower)):
                        
                        # Get media files for this item
                        for media in item.get('Media', []):
                            for part in media.get('Part', []):
                                matches.append({
                                    'rating_key': item.get('ratingKey'),
                                    'title': item.get('title'),
                                    'file_path': part.get('file', ''),
                                    'media_id': media.get('id'),
                                    'part_id': part.get('id')
                                })
                                print(f"   ✅ Found match: '{item.get('title')}' (Rating Key: {item.get('ratingKey')})")
                
                if matches:
                    return matches
            
            # If exact search fails, try broader search without title parameter
            response = self.session.get(
                f"{self.plex_url}/library/sections/{library_key}/all",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                
                # Look through all items for fuzzy matches
                for item in data.get('MediaContainer', {}).get('Metadata', []):
                    item_title = item.get('title', '').lower()
                    search_lower = search_term.lower()
                    
                    # More flexible matching
                    if self._fuzzy_title_match(item_title, search_lower):
                        for media in item.get('Media', []):
                            for part in media.get('Part', []):
                                matches.append({
                                    'rating_key': item.get('ratingKey'),
                                    'title': item.get('title'),
                                    'file_path': part.get('file', ''),
                                    'media_id': media.get('id'),
                                    'part_id': part.get('id')
                                })
                                print(f"   ✅ Fuzzy match: '{item.get('title')}' (Rating Key: {item.get('ratingKey')})")
                
                return matches
                
            else:
                print(f"   ❌ Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error in library search: {e}")
            return []
    
    def _fuzzy_title_match(self, title1, title2):
        """Check if two titles are similar enough to be considered a match"""
        import re
        
        # Remove common words and punctuation for comparison
        def clean_title(title):
            # Remove articles, punctuation, and extra spaces
            cleaned = re.sub(r'[^\w\s]', ' ', title.lower())
            cleaned = re.sub(r'\b(a|an|the)\b', '', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned
        
        clean1 = clean_title(title1)
        clean2 = clean_title(title2)
        
        # Check various similarity conditions
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        # If either title is contained in the other after cleaning
        if clean1 in clean2 or clean2 in clean1:
            return True
        
        # If most words match
        if words1 and words2:
            common_words = words1.intersection(words2)
            if len(common_words) >= min(len(words1), len(words2)) * 0.7:
                return True
        
        return False
    
    def get_media_subtitles(self, rating_key):
        """Get all subtitles for a media item"""
        try:
            response = self.session.get(
                f"{self.plex_url}/library/metadata/{rating_key}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                subtitles = []
                
                for item in data.get('MediaContainer', {}).get('Metadata', []):
                    for media in item.get('Media', []):
                        for part in media.get('Part', []):
                            for stream in part.get('Stream', []):
                                if stream.get('streamType') == 3:  # Subtitle stream
                                    subtitles.append({
                                        'id': stream.get('id'),
                                        'language': stream.get('language', 'unknown'),
                                        'language_code': stream.get('languageCode', ''),
                                        'codec': stream.get('codec', ''),
                                        'title': stream.get('title', ''),
                                        'external': stream.get('external', False),
                                        'file': stream.get('file', ''),
                                        'selected': stream.get('selected', False)
                                    })
                
                return subtitles
            
            return []
            
        except Exception as e:
            print(f"❌ Error getting subtitles: {e}")
            return []
    
    def set_preferred_subtitle(self, part_id, subtitle_id):
        """Set preferred subtitle for a media item"""
        try:
            # Correct URL for setting subtitle preference
            # Use the part ID and stream ID to set subtitle selection
            url = f"{self.plex_url}/library/parts/{part_id}"
            
            # Set the subtitle stream as selected
            params = {
                f"subtitleStreamID": subtitle_id,
                "allParts": "1"
            }
            
            response = self.session.put(
                url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                print(f"✅ Subtitle preference updated")
                return True
            else:
                print(f"❌ Failed to set subtitle: {response.status_code}")
                # Try alternative method
                return self._set_subtitle_alternative_method(part_id, subtitle_id)
                
        except Exception as e:
            print(f"❌ Error setting subtitle: {e}")
            return False
    
    def _set_subtitle_alternative_method(self, part_id, subtitle_id):
        """Alternative method to set subtitle using different API approach"""
        try:
            print("🔄 Trying alternative subtitle setting method...")
            
            # Try using the timeline endpoint
            url = f"{self.plex_url}/:/timeline"
            
            params = {
                "ratingKey": part_id,
                "state": "stopped",
                "time": "0",
                "duration": "0",
                "subtitleStreamID": subtitle_id
            }
            
            response = self.session.get(
                url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                print(f"✅ Subtitle set via alternative method")
                return True
            else:
                print(f"❌ Alternative method failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in alternative method: {e}")
            return False
    
    def find_and_set_synced_subtitle(self, video_path, series_title=None):
        """Find synced subtitle and set it as preferred"""
        try:
            print(f"\n🎬 PLEX SUBTITLE AUTO-CONFIGURATION")
            print("="*50)
            print(f"📁 Video: {os.path.basename(video_path)}")
            if series_title:
                print(f"📺 Series: {series_title}")
            
            # Find the media item in Plex
            media_item = self.search_media_by_path(video_path, series_title)
            
            if not media_item:
                return False, "Media not found in Plex"
            
            print(f"🎯 Found in Plex: {media_item['title']}")
            print(f"📊 Rating Key: {media_item['rating_key']}")
            
            # Get all subtitles for this media
            subtitles = self.get_media_subtitles(media_item['rating_key'])
            
            if not subtitles:
                return False, "No subtitles found"
            
            print(f"📄 Found {len(subtitles)} subtitle streams:")
            
            # Look for synced Dutch subtitle
            synced_subtitle = None
            
            for subtitle in subtitles:
                display_name = subtitle.get('title', subtitle.get('file', f"Stream {subtitle['id']}"))
                language = subtitle.get('language', 'unknown')
                selected = "✅" if subtitle.get('selected') else "⭕"
                
                print(f"   {selected} {display_name} ({language})")
                
                # Check if this is a synced Dutch subtitle
                subtitle_file = subtitle.get('file', '')
                
                # Enhanced detection for synced Dutch subtitles
                is_dutch = (subtitle.get('language_code') == 'nl' or 
                           subtitle.get('language') == 'Dutch' or
                           subtitle.get('language') == 'Nederlands')
                
                # Look for synced indicators in various places
                has_synced_indicator = (
                    'synced' in display_name.lower() or
                    'synced' in subtitle_file.lower() or
                    '.nl.synced.' in subtitle_file.lower() or
                    '.synced.nl.' in subtitle_file.lower() or
                    '.synced.srt' in subtitle_file.lower()
                )
                
                # Debug info
                print(f"      File: {subtitle_file}")
                print(f"      Dutch: {is_dutch}, Synced indicator: {has_synced_indicator}")
                
                if is_dutch:
                    # Prioritize synced subtitles, but accept any Dutch subtitle if no synced found
                    if has_synced_indicator:
                        synced_subtitle = subtitle
                        print(f"   🎯 Found synced Dutch subtitle!")
                        break
                    elif synced_subtitle is None:
                        # Keep as backup if no synced subtitle found
                        synced_subtitle = subtitle
                        print(f"   📝 Found Dutch subtitle (backup choice)")
            
            if not synced_subtitle:
                return False, "No Dutch subtitle found"
            
            # Determine if we found a synced or regular subtitle
            subtitle_type = "synced" if 'synced' in synced_subtitle.get('file', '').lower() else "Dutch"
            
            # Set this subtitle as preferred
            print(f"🔄 Setting {subtitle_type} subtitle as preferred...")
            success = self.set_preferred_subtitle(
                media_item['part_id'], 
                synced_subtitle['id']
            )
            
            if success:
                return True, f"{subtitle_type.capitalize()} subtitle set as preferred"
            else:
                return False, "Failed to set subtitle preference"
                
        except Exception as e:
            print(f"❌ Error configuring Plex subtitle: {e}")
            return False, str(e)
    
    def auto_configure_synced_files(self, base_directory):
        """Auto-configure all synced files in a directory"""
        try:
            print(f"\n🚀 BULK PLEX SUBTITLE CONFIGURATION")
            print("="*50)
            print(f"📁 Directory: {base_directory}")
            
            # Find all .synced.nl.srt files
            synced_files = []
            
            for root, dirs, files in os.walk(base_directory):
                for file in files:
                    if file.endswith('.synced.nl.srt'):
                        # Find corresponding video file
                        video_name = file.replace('.synced.nl.srt', '')
                        
                        # Look for video files with this name
                        for ext in ['.mkv', '.mp4', '.avi', '.m4v', '.mov']:
                            video_file = os.path.join(root, video_name + ext)
                            if os.path.exists(video_file):
                                synced_files.append(video_file)
                                break
            
            print(f"🎯 Found {len(synced_files)} videos with synced subtitles")
            
            if not synced_files:
                return 0, 0
            
            success_count = 0
            failed_count = 0
            
            for i, video_file in enumerate(synced_files, 1):
                print(f"\n📺 Processing {i}/{len(synced_files)}: {os.path.basename(video_file)}")
                
                success, message = self.find_and_set_synced_subtitle(video_file)
                
                if success:
                    success_count += 1
                    print(f"   ✅ {message}")
                else:
                    failed_count += 1
                    print(f"   ❌ {message}")
            
            print(f"\n🎉 BULK CONFIGURATION COMPLETED")
            print(f"✅ Successfully configured: {success_count}")
            print(f"❌ Failed: {failed_count}")
            
            return success_count, failed_count
            
        except Exception as e:
            print(f"❌ Error in bulk configuration: {e}")
            return 0, 0