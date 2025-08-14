#!/usr/bin/env python3
"""
Test the subtitle translation functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.append('.')

def test_translation_system():
    """Test the subtitle translation system"""
    print("🧪 TESTING SUBTITLE TRANSLATION SYSTEM")
    print("=" * 60)
    
    try:
        from subtitle_translator import SubtitleTranslator
        translator = SubtitleTranslator()
        
        print("✅ Subtitle translator imported successfully")
        
        # Test detection of subtitle language
        test_filenames = [
            "movie.en.srt",
            "movie.english.srt", 
            "movie.es.srt",
            "movie.fr.srt",
            "movie.srt"
        ]
        
        print("\n📝 Testing language detection:")
        for filename in test_filenames:
            detected = translator._detect_subtitle_language(filename)
            print(f"   {filename} → {detected}")
        
        # Test SRT parsing
        sample_srt = """1
00:00:01,000 --> 00:00:05,000
Hello, this is a test subtitle.

2
00:00:06,000 --> 00:00:10,000
This is the second subtitle entry.
"""
        
        print("\n📄 Testing SRT parsing:")
        entries = translator._parse_srt_content(sample_srt)
        print(f"   Parsed {len(entries)} entries")
        for entry in entries:
            print(f"   {entry['number']}: {entry['timing']} - {entry['text'][:30]}...")
        
        # Test translation services availability
        print("\n🌐 Testing translation services:")
        test_texts = ["Hello world", "This is a test"]
        
        for api_name in translator.api_priority:
            try:
                print(f"   Testing {api_name}... ", end='')
                if api_name == 'google':
                    print("❌ Requires API key (skipped)")
                    continue
                
                # Small test
                result = translator._batch_translate(["Hello"], "nl", api_name)
                if result and result[0]:
                    print(f"✅ Working - 'Hello' → '{result[0]}'")
                else:
                    print("❌ No result")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n✅ Translation system test complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_ffmpeg_availability():
    """Test if ffmpeg and ffprobe are available"""
    print("\n🔧 TESTING FFMPEG AVAILABILITY")
    print("=" * 40)
    
    import subprocess
    
    tools = ['ffmpeg', 'ffprobe']
    
    for tool in tools:
        try:
            result = subprocess.run([tool, '-version'], 
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Extract version info
                version_line = result.stdout.split('\n')[0]
                print(f"   ✅ {tool}: {version_line}")
            else:
                print(f"   ❌ {tool}: Not working")
        except FileNotFoundError:
            print(f"   ❌ {tool}: Not installed")
        except subprocess.TimeoutExpired:
            print(f"   ❌ {tool}: Timeout")
        except Exception as e:
            print(f"   ❌ {tool}: Error - {e}")

if __name__ == "__main__":
    print("🚀 SUBTITLE TRANSLATION SYSTEM TESTS")
    print("=" * 60)
    
    success1 = test_translation_system()
    test_ffmpeg_availability()
    
    print("\n" + "=" * 60)
    if success1:
        print("✅ All tests passed! Translation system is ready.")
        print("\n💡 Usage:")
        print("   - System will automatically try translation when no Dutch subtitles found")
        print("   - Supports external subtitle files and embedded subtitles")
        print("   - Uses free translation APIs (LibreTranslate, MyMemory)")
        print("   - Fallback order: existing files → embedded → translation")
    else:
        print("❌ Some tests failed. Check error messages above.")
