from flask import Flask, request, jsonify, send_from_directory
from recap_generator import FantasyRecapGenerator
import os

# Initialize the Flask app
app = Flask(__name__, static_folder='frontend')

# Define the API endpoint for generating a recap
@app.route('/api/generate_recap', methods=['POST'])
def generate_recap_endpoint():
    data = request.get_json()
    year = data.get('year')
    week = data.get('week')

    if not year or not week:
        return jsonify({"error": "Year and week are required"}), 400

    try:
        # Your existing class does all the hard work!
        generator = FantasyRecapGenerator(year=year, week=week)
        
        # We need to modify your class to RETURN the summary and filename
        # instead of just printing them.
        summary_text, audio_filename = generator.generate_weekly_recap()
        
        return jsonify({
            "summary": summary_text,
            "audioUrl": f"/audio/{audio_filename}" # URL for the frontend to use
        })
    except Exception as e:
        # Return a proper error response
        return jsonify({"error": str(e)}), 500

# Define a route to serve the generated audio files
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('.', filename) # Serves files from the root project folder

# A simple route for the homepage
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)