#!/bin/bash

# Fantasy Football Weekly Recap Generator - Runner Script

echo "🎯 Fantasy Football Weekly Recap Generator"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please run setup.py first or create a .env file with your credentials"
    exit 1
fi

# Run the recap generator
echo "🚀 Starting recap generation..."
python3 recap_generator.py 