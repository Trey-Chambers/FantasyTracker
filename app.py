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

app = Flask(__name__, static_folder='frontend')
CORS(app)  # Enable CORS for frontend communication

# No global recap generator needed - we'll create instances per request

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_file('frontend/index.html')

@app.route('/scripts.js')
def serve_scripts():
    """Serve the JavaScript file."""
    return send_file('frontend/scripts.js')

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
        # Create a temporary generator to get league info
        generator = FantasyRecapGenerator()
        league_name = generator.league.settings.name
        current_week = generator.league.current_week
        
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
        # Get year, week, and personality from the frontend's request
        data = request.get_json()
        year = data.get('year')
        week = data.get('week')
        personality = data.get('personality', 'SVP')  # Default to SVP if not provided

        if not year or not week:
            return jsonify({'error': 'Year and week are required'}), 400

        # Create a new generator instance FOR THIS REQUEST with the specific year, week, and personality
        generator = FantasyRecapGenerator(year=year, week=week, personality=personality)
        
        # Generate the recap
        summary, audio_filename = generator.generate_weekly_recap()
        
        return jsonify({
            'success': True,
            'summary': summary,
            'audio_filename': audio_filename,
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

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    logger.info("Open your browser to: http://localhost:5000")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)