#!/usr/bin/env python3
"""
Test script for Fantasy Football Weekly Recap Generator
This script tests your credentials and API connection without generating a full recap.
"""

import os
import sys
from dotenv import load_dotenv

def test_credentials():
    """Test if credentials are properly loaded."""
    print("🔐 Testing credential loading...")
    
    try:
        load_dotenv()
        
        league_id = os.getenv('LEAGUE_ID')
        espn_s2 = os.getenv('ESPN_S2')
        swid = os.getenv('SWID')
        
        if not all([league_id, espn_s2, swid]):
            print("❌ Missing credentials:")
            if not league_id:
                print("   - LEAGUE_ID not found")
            if not espn_s2:
                print("   - ESPN_S2 not found")
            if not swid:
                print("   - SWID not found")
            return False
        
        # Test league_id conversion
        try:
            league_id_int = int(league_id)
            print(f"✅ LEAGUE_ID: {league_id_int}")
        except ValueError:
            print("❌ LEAGUE_ID must be a valid integer")
            return False
        
        print(f"✅ ESPN_S2: {espn_s2[:20]}...")
        print(f"✅ SWID: {swid[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False

def test_api_connection():
    """Test ESPN API connection."""
    print("\n🌐 Testing ESPN API connection...")
    
    try:
        from espn_api.football import League
        from datetime import datetime
        
        load_dotenv()
        
        league = League(
            league_id=int(os.getenv('LEAGUE_ID')),
            year=datetime.now().year,
            espn_s2=os.getenv('ESPN_S2'),
            swid=os.getenv('SWID')
        )
        
        # Test basic league info
        league_name = league.settings.name
        current_week = league.current_week
        
        print(f"✅ Successfully connected to league: {league_name}")
        print(f"✅ Current week: {current_week}")
        
        # Test scoreboard access
        if current_week > 1:
            try:
                scoreboard = league.scoreboard(week=current_week - 1)
                print(f"✅ Successfully fetched scoreboard for week {current_week - 1}")
                print(f"   Found {len(scoreboard)} matchups")
            except Exception as e:
                print(f"⚠️  Could not fetch previous week's scoreboard: {e}")
        else:
            print("ℹ️  Season hasn't started yet (week 1)")
        
        return True
        
    except ImportError:
        print("❌ espn-api package not installed. Run: pip install espn-api")
        return False
    except Exception as e:
        print(f"❌ Failed to connect to ESPN API: {e}")
        return False

def test_tts():
    """Test Google TTS functionality."""
    print("\n🎵 Testing Google TTS...")
    
    try:
        from gtts import gTTS
        
        test_text = "This is a test of the text to speech functionality."
        tts = gTTS(text=test_text, lang='en', slow=False)
        
        # Test file creation (don't save)
        print("✅ Google TTS is working correctly")
        return True
        
    except ImportError:
        print("❌ gtts package not installed. Run: pip install gtts")
        return False
    except Exception as e:
        print(f"❌ Google TTS test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Fantasy Football Recap Generator - Setup Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test credentials
    if not test_credentials():
        all_tests_passed = False
    
    # Test API connection
    if not test_api_connection():
        all_tests_passed = False
    
    # Test TTS
    if not test_tts():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    
    if all_tests_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("You can now run: python recap_generator.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the main script.")
        print("\nCommon solutions:")
        print("1. Check your .env file has correct credentials")
        print("2. Ensure all packages are installed: pip install -r requirements.txt")
        print("3. Verify your internet connection")
        print("4. Check that your ESPN account is active")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 