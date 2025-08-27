#!/usr/bin/env python3
"""
Setup script for Fantasy Football Weekly Recap Generator
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please try running:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

def create_env_template():
    """Create a template .env file if it doesn't exist."""
    env_file = ".env"
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return
    
    print("📝 Creating .env template file...")
    template = """# ESPN Fantasy Football API Credentials
# Fill in your actual values below

# Your ESPN Fantasy Football League ID (found in the URL when viewing your league)
LEAGUE_ID=123456789

# ESPN S2 Cookie Value (found in browser developer tools under espn.com cookies)
ESPN_S2=your_espn_s2_cookie_value_here

# SWID Cookie Value (found in browser developer tools under espn.com cookies)
SWID=your_swid_cookie_value_here

# AI and Voice Generation API Keys
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(template)
        print("✅ .env template file created successfully!")
        print("⚠️  IMPORTANT: Edit .env file with your actual credentials before running the script")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def main():
    """Main setup function."""
    print("🎯 Fantasy Football Weekly Recap Generator - Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Create .env template
    create_env_template()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your actual ESPN credentials")
    print("2. Run: python recap_generator.py")
    print("\nFor detailed instructions, see README.md")
    print("=" * 50)

if __name__ == "__main__":
    main() 