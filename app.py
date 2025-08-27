#!/usr/bin/env python3
"""
Flask Backend for Fantasy Football Weekly Recap Generator
Provides API endpoints for the web frontend to interact with the recap generator.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
from datetime import datetime
import traceback

# Import our refactored recap generator
from recap_generator import FantasyRecapGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global instance of the recap generator
recap_generator = None

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_file('frontend/index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Fantasy Football Recap Generator API'
    })

@app.route('/api/league-info')
def get_league_info():
    """Get basic league information."""
    try:
        global recap_generator
        
        if recap_generator is None:
            return jsonify({'error': 'Recap generator not initialized'}), 500
        
        league_name = recap_generator.league.settings.name
        current_week = recap_generator.league.current_week
        
        return jsonify({
            'league_name': league_name,
            'current_week': current_week,
            'target_week': current_week - 1 if current_week > 1 else None
        })
        
    except Exception as e:
        logger.error(f"Error getting league info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-recap', methods=['POST'])
def generate_recap():
    """Generate a weekly recap."""
    try:
        global recap_generator
        
        if recap_generator is None:
            return jsonify({'error': 'Recap generator not initialized'}), 500
        
        # Generate the recap
        summary, audio_filename = recap_generator.generate_weekly_recap()
        
        # Get the full path to the audio file
        audio_path = os.path.join(os.getcwd(), audio_filename)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'audio_filename': audio_filename,
            'audio_path': audio_path,
            'message': 'Recap generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error generating recap: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to generate recap'
        }), 500

@app.route('/api/audio/<filename>')
def get_audio(filename):
    """Serve audio files."""
    try:
        # Security: Only allow MP3 files
        if not filename.endswith('.mp3'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Check if file exists
        file_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        return send_file(file_path, mimetype='audio/mpeg')
        
    except Exception as e:
        logger.error(f"Error serving audio file {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/available-audio')
def get_available_audio():
    """Get list of available audio files."""
    try:
        audio_files = []
        for file in os.listdir('.'):
            if file.endswith('.mp3') and file.startswith('recap_week_'):
                audio_files.append({
                    'filename': file,
                    'week': file.replace('recap_week_', '').replace('.mp3', ''),
                    'size': os.path.getsize(file),
                    'created': datetime.fromtimestamp(os.path.getctime(file)).isoformat()
                })
        
        # Sort by week number
        audio_files.sort(key=lambda x: int(x['week']))
        
        return jsonify({
            'audio_files': audio_files,
            'count': len(audio_files)
        })
        
    except Exception as e:
        logger.error(f"Error getting available audio files: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

def initialize_recap_generator():
    """Initialize the recap generator on startup."""
    global recap_generator
    try:
        logger.info("Initializing Fantasy Recap Generator...")
        recap_generator = FantasyRecapGenerator()
        logger.info("Recap generator initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize recap generator: {e}")
        return False

if __name__ == '__main__':
    # Initialize the recap generator
    if not initialize_recap_generator():
        logger.error("Failed to initialize recap generator. Exiting.")
        exit(1)
    
    logger.info("Starting Flask server...")
    logger.info("Open your browser to: http://localhost:5000")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)