"""
Subtitle Translation Module
Automatically generates Dutch subtitles by translating existing subtitles in other languages

This module provides comprehensive subtitle translation capabilities:
- Finds existing subtitle files alongside video files
- Extracts embedded subtitles from video files using ffmpeg
- Translates subtitles using multiple free APIs (LibreTranslate, MyMemory)
- Supports multiple subtitle formats (.srt, .vtt, .ass, .ssa, .sub)
- Handles batch translation with rate limiting
- Provides automatic language detection from filenames

Main workflow:
1. Search for existing subtitle files next to video
2. If not found, extract embedded subtitles from video
3. Select best source subtitle (prioritizing English)
4. Translate to target language using available APIs
5. Generate properly formatted output subtitle file

Dependencies:
- requests (for API calls)
- ffmpeg/ffprobe (for embedded subtitle extraction)
- Standard Python libraries (os, re, time, subprocess, json)
"""

import os
import re
import time
import subprocess
import requests
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class SubtitleTranslator:
    """
    Automatic subtitle translation system
    
    Provides intelligent subtitle translation capabilities by:
    - Discovering existing subtitle files and embedded subtitles
    - Selecting optimal source language (prioritizing English)
    - Translating using multiple free APIs with fallback support
    - Generating properly formatted SRT output files
    
    Attributes:
        config (dict): Configuration settings for translation
        supported_formats (list): Supported subtitle file formats
        translation_apis (dict): Available translation API handlers
        api_priority (list): Priority order for trying translation APIs
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.supported_formats = ['.srt', '.vtt', '.ass', '.ssa', '.sub']
        self.translation_apis = {
            'google': self._translate_google,
            'libre': self._translate_libre,
            'mymemory': self._translate_mymemory
        }
        
        # Translation service priority (free services first)
        self.api_priority = ['libre', 'mymemory', 'google']
        
    def find_and_translate_subtitles(self, video_path: str, target_language: str = 'nl') -> Optional[str]:
        """
        Main function: Find existing subtitles and translate them to target language
        
        This is the primary entry point for subtitle translation. It follows a
        comprehensive workflow to find and translate subtitles:
        
        1. Search for existing subtitle files next to the video
        2. If none found, extract embedded subtitles from video file
        3. Select the best source subtitle (prioritizing English)
        4. Translate using available APIs with automatic fallback
        5. Generate and save translated subtitle file
        
        Args:
            video_path (str): Full path to the video file
            target_language (str): Target language code (default: 'nl' for Dutch)
            
        Returns:
            str: Path to successfully created translated subtitle file
            None: If no suitable source subtitles found or translation failed
            
        Example:
            translator = SubtitleTranslator()
            result = translator.find_and_translate_subtitles('/path/to/movie.mkv', 'nl')
            if result:
                print(f"Dutch subtitles created: {result}")
        """
        print(f"\n🌐 SUBTITLE TRANSLATION")
        print("=" * 50)
        print(f"📁 Video: {os.path.basename(video_path)}")
        print(f"🎯 Target language: {target_language}")
        
        # Step 1: Look for existing subtitle files
        existing_subs = self._find_existing_subtitles(video_path)
        
        if existing_subs:
            print(f"✅ Found {len(existing_subs)} existing subtitle file(s)")
            for sub_path, lang in existing_subs:
                print(f"   📄 {os.path.basename(sub_path)} ({lang})")
                
            # Try to translate the best candidate
            best_subtitle = self._select_best_subtitle(existing_subs, target_language)
            if best_subtitle:
                return self._translate_subtitle_file(best_subtitle[0], target_language)
        
        # Step 2: Extract embedded subtitles if no external files found
        print("🔍 Looking for embedded subtitles...")
        embedded_subs = self._extract_embedded_subtitles(video_path)
        
        if embedded_subs:
            print(f"✅ Found {len(embedded_subs)} embedded subtitle track(s)")
            for sub_path, lang in embedded_subs:
                print(f"   📄 {os.path.basename(sub_path)} ({lang})")
                
            # Try to translate the best embedded subtitle
            best_embedded = self._select_best_subtitle(embedded_subs, target_language)
            if best_embedded:
                return self._translate_subtitle_file(best_embedded[0], target_language)
        
        print("❌ No suitable subtitles found for translation")
        return None
    
    def _find_existing_subtitles(self, video_path: str) -> List[Tuple[str, str]]:
        """Find existing subtitle files next to the video"""
        video_dir = os.path.dirname(video_path)
        video_base = os.path.splitext(os.path.basename(video_path))[0]
        
        subtitle_files = []
        
        # Look for subtitle files with same base name
        for file in os.listdir(video_dir):
            if any(file.lower().endswith(ext) for ext in self.supported_formats):
                # Check if it belongs to this video
                file_base = os.path.splitext(file)[0]
                
                # Match patterns like: movie.en.srt, movie.english.srt, movie.srt
                if file_base.startswith(video_base):
                    sub_path = os.path.join(video_dir, file)
                    language = self._detect_subtitle_language(file)
                    subtitle_files.append((sub_path, language))
        
        return subtitle_files
    
    def _extract_embedded_subtitles(self, video_path: str) -> List[Tuple[str, str]]:
        """Extract embedded subtitles from video file using ffmpeg"""
        try:
            # Get subtitle stream info
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_streams', '-select_streams', 's', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return []
            
            stream_info = json.loads(result.stdout)
            subtitle_streams = stream_info.get('streams', [])
            
            if not subtitle_streams:
                return []
            
            print(f"🔍 Found {len(subtitle_streams)} embedded subtitle stream(s)")
            
            extracted_files = []
            video_base = os.path.splitext(video_path)[0]
            
            for i, stream in enumerate(subtitle_streams):
                # Get language info
                language = stream.get('tags', {}).get('language', f'track_{i}')
                title = stream.get('tags', {}).get('title', '')
                
                print(f"   📺 Stream {i}: {language} - {title}")
                
                # Skip if it's already Dutch
                if language.lower() in ['nl', 'dut', 'dutch', 'netherlands']:
                    continue
                
                # Extract subtitle to file
                output_path = f"{video_base}.extracted_{i}_{language}.srt"
                extract_cmd = [
                    'ffmpeg', '-i', video_path, '-map', f'0:s:{i}', 
                    '-c:s', 'srt', '-y', output_path
                ]
                
                try:
                    extract_result = subprocess.run(extract_cmd, capture_output=True, text=True)
                    if extract_result.returncode == 0 and os.path.exists(output_path):
                        print(f"   ✅ Extracted: {os.path.basename(output_path)}")
                        extracted_files.append((output_path, language))
                    else:
                        print(f"   ❌ Failed to extract stream {i}")
                except Exception as e:
                    print(f"   ❌ Error extracting stream {i}: {e}")
            
            return extracted_files
            
        except Exception as e:
            print(f"❌ Error extracting embedded subtitles: {e}")
            return []
    
    def _detect_subtitle_language(self, filename: str) -> str:
        """Detect language from subtitle filename"""
        filename_lower = filename.lower()
        
        # Language code patterns
        language_patterns = {
            'en': ['en', 'eng', 'english'],
            'es': ['es', 'spa', 'spanish', 'espanol'],
            'fr': ['fr', 'fra', 'french', 'francais'],
            'de': ['de', 'ger', 'german', 'deutsch'],
            'it': ['it', 'ita', 'italian', 'italiano'],
            'pt': ['pt', 'por', 'portuguese', 'portugues'],
            'ru': ['ru', 'rus', 'russian'],
            'zh': ['zh', 'chi', 'chinese', 'mandarin'],
            'ja': ['ja', 'jpn', 'japanese'],
            'ko': ['ko', 'kor', 'korean']
        }
        
        for lang_code, patterns in language_patterns.items():
            for pattern in patterns:
                if f'.{pattern}.' in filename_lower or filename_lower.endswith(f'.{pattern}.srt'):
                    return lang_code
        
        return 'unknown'
    
    def _select_best_subtitle(self, subtitles: List[Tuple[str, str]], target_language: str) -> Optional[Tuple[str, str]]:
        """Select the best subtitle file for translation"""
        if not subtitles:
            return None
        
        # Priority order for source languages (English is usually best quality)
        language_priority = ['en', 'english', 'eng', 'es', 'fr', 'de', 'it', 'unknown']
        
        # Sort by language priority
        def get_priority(subtitle_info):
            _, language = subtitle_info
            try:
                return language_priority.index(language.lower())
            except ValueError:
                return len(language_priority)  # Unknown languages go last
        
        sorted_subtitles = sorted(subtitles, key=get_priority)
        return sorted_subtitles[0]
    
    def _translate_subtitle_file(self, subtitle_path: str, target_language: str) -> Optional[str]:
        """Translate subtitle file to target language"""
        print(f"\n🔄 Translating subtitle file...")
        print(f"📄 Source: {os.path.basename(subtitle_path)}")
        
        # Read subtitle content
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(subtitle_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                print(f"❌ Error reading subtitle file: {e}")
                return None
        
        # Parse subtitle content
        subtitle_entries = self._parse_srt_content(content)
        if not subtitle_entries:
            print("❌ No subtitle entries found")
            return None
        
        print(f"📊 Found {len(subtitle_entries)} subtitle entries")
        
        # Translate entries in batches
        translated_entries = self._translate_subtitle_entries(subtitle_entries, target_language)
        
        if not translated_entries:
            print("❌ Translation failed")
            return None
        
        # Generate output file
        output_path = self._generate_translated_filename(subtitle_path, target_language)
        
        # Write translated subtitle file
        success = self._write_srt_file(output_path, translated_entries)
        
        if success:
            print(f"✅ Translation complete: {os.path.basename(output_path)}")
            return output_path
        else:
            print("❌ Failed to write translated file")
            return None
    
    def _parse_srt_content(self, content: str) -> List[Dict]:
        """Parse SRT subtitle content"""
        entries = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    # Extract entry number
                    entry_num = int(lines[0])
                    
                    # Extract timing
                    timing = lines[1]
                    
                    # Extract text (everything after timing)
                    text = '\n'.join(lines[2:])
                    
                    entries.append({
                        'number': entry_num,
                        'timing': timing,
                        'text': text
                    })
                except (ValueError, IndexError):
                    continue
        
        return entries
    
    def _translate_subtitle_entries(self, entries: List[Dict], target_language: str) -> List[Dict]:
        """Translate subtitle entries using available APIs"""
        translated_entries = []
        
        # Group entries for batch translation (API efficiency)
        batch_size = 50
        total_batches = (len(entries) + batch_size - 1) // batch_size
        
        print(f"🔄 Translating in {total_batches} batch(es)...")
        
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"   📦 Batch {batch_num}/{total_batches} ({len(batch)} entries)")
            
            # Extract texts for translation
            texts_to_translate = [entry['text'] for entry in batch]
            
            # Try translation APIs in priority order
            translated_texts = None
            for api_name in self.api_priority:
                try:
                    print(f"   🌐 Trying {api_name} API...")
                    translated_texts = self._batch_translate(texts_to_translate, target_language, api_name)
                    if translated_texts:
                        print(f"   ✅ Success with {api_name}")
                        break
                except Exception as e:
                    print(f"   ❌ {api_name} failed: {e}")
                    continue
            
            if not translated_texts:
                print(f"   ❌ All translation APIs failed for batch {batch_num}")
                return []
            
            # Combine with timing info
            for j, entry in enumerate(batch):
                translated_entry = entry.copy()
                translated_entry['text'] = translated_texts[j] if j < len(translated_texts) else entry['text']
                translated_entries.append(translated_entry)
            
            # Rate limiting
            time.sleep(1)
        
        return translated_entries
    
    def _batch_translate(self, texts: List[str], target_language: str, api_name: str) -> List[str]:
        """Translate batch of texts using specified API"""
        api_function = self.translation_apis.get(api_name)
        if not api_function:
            raise ValueError(f"Unknown API: {api_name}")
        
        return api_function(texts, target_language)
    
    def _translate_libre(self, texts: List[str], target_language: str) -> List[str]:
        """Translate using LibreTranslate (free, self-hosted option)"""
        # LibreTranslate public instance (rate limited)
        url = "https://libretranslate.de/translate"
        
        translated_texts = []
        
        for text in texts:
            if not text.strip():
                translated_texts.append(text)
                continue
            
            data = {
                "q": text,
                "source": "auto",
                "target": target_language,
                "format": "text"
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                translated_texts.append(result.get('translatedText', text))
            else:
                raise Exception(f"HTTP {response.status_code}")
            
            time.sleep(0.5)  # Rate limiting
        
        return translated_texts
    
    def _translate_mymemory(self, texts: List[str], target_language: str) -> List[str]:
        """Translate using MyMemory API (free tier available)"""
        base_url = "https://api.mymemory.translated.net/get"
        
        translated_texts = []
        
        for text in texts:
            if not text.strip():
                translated_texts.append(text)
                continue
            
            params = {
                "q": text,
                "langpair": f"en|{target_language}"
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('responseStatus') == 200:
                    translated_text = result.get('responseData', {}).get('translatedText', text)
                    translated_texts.append(translated_text)
                else:
                    raise Exception(f"API error: {result.get('responseDetails', 'Unknown error')}")
            else:
                raise Exception(f"HTTP {response.status_code}")
            
            time.sleep(0.3)  # Rate limiting
        
        return translated_texts
    
    def _translate_google(self, texts: List[str], target_language: str) -> List[str]:
        """Translate using Google Translate API (requires API key)"""
        # This would require Google Cloud Translation API key
        # For now, raise exception to try other services
        raise Exception("Google Translate API requires authentication key")
    
    def _generate_translated_filename(self, original_path: str, target_language: str) -> str:
        """Generate filename for translated subtitle"""
        base_path = os.path.splitext(original_path)[0]
        
        # Remove any existing language codes
        base_path = re.sub(r'\.(en|es|fr|de|it|pt|ru|zh|ja|ko|extracted_\d+_\w+)$', '', base_path)
        
        return f"{base_path}.{target_language}.translated.srt"
    
    def _write_srt_file(self, output_path: str, entries: List[Dict]) -> bool:
        """Write translated entries to SRT file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for entry in entries:
                    f.write(f"{entry['number']}\n")
                    f.write(f"{entry['timing']}\n")
                    f.write(f"{entry['text']}\n\n")
            
            return True
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False
    
    def cleanup_extracted_files(self, video_path: str):
        """Clean up temporarily extracted subtitle files"""
        video_dir = os.path.dirname(video_path)
        video_base = os.path.splitext(os.path.basename(video_path))[0]
        
        # Look for extracted files
        for file in os.listdir(video_dir):
            if file.startswith(f"{video_base}.extracted_") and file.endswith('.srt'):
                file_path = os.path.join(video_dir, file)
                try:
                    os.remove(file_path)
                    print(f"🗑️ Cleaned up: {file}")
                except Exception as e:
                    print(f"⚠️ Could not remove {file}: {e}")
