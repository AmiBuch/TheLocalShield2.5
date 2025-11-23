#!/usr/bin/env python3
"""
Emergency Alert Generator using Google Gemini
Converts voice transcriptions into structured emergency messages
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyD5uLyJo-7vbkMwzVPjPoicbLFzzpuaqcg')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_emergency_prompt(transcription, location=None):
    """Generate prompt for Gemini to create emergency alert"""
    location_text = f"\nLocation data: {location}" if location else ""
    
    prompt = f"""You are an emergency message processor. A person in danger has sent a voice message that was transcribed (may contain transcription errors).

Your task: Generate a detailed, clear emergency alert message that their emergency contacts will receive via SMS. Include ALL relevant information.

Voice transcription: "{transcription}"{location_text}

Create an emergency alert message that includes:
- Clear statement that this is an emergency
- What is happening (situation/threat)
- Exact location details if mentioned
- Any descriptions of people/vehicles if mentioned
- Current actions the person is taking
- Sense of urgency and recommended actions for contacts

Format the message to be clear, actionable, and urgent. Keep it under 500 characters for SMS compatibility.

Emergency Alert Message:"""
    return prompt

@app.route('/generate-alert', methods=['POST'])
def generate_alert():
    """
    Generate emergency alert from transcription
    Expects JSON with 'transcription' and optional 'location'
    """
    try:
        data = request.get_json()
        if not data or 'transcription' not in data:
            return jsonify({'error': 'No transcription provided'}), 400
        
        transcription = data['transcription']
        location = data.get('location')
        
        logger.info(f"Generating emergency alert for transcription: {transcription[:50]}...")
        
        # Generate prompt
        prompt = generate_emergency_prompt(transcription, location)
        
        # Call Gemini API
        response = model.generate_content(prompt)
        emergency_message = response.text.strip()
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        emergency_message = f"{emergency_message}\n\nTime sent: {timestamp}"
        
        logger.info("Emergency alert generated successfully")
        
        return jsonify({
            'success': True,
            'alert_message': emergency_message,
            'original_transcription': transcription,
            'timestamp': timestamp
        })
        
    except Exception as e:
        logger.error(f"Error generating alert: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Gemini connection
        test_response = model.generate_content("Test")
        gemini_status = "connected"
    except:
        gemini_status = "error"
    
    return jsonify({
        'status': 'healthy',
        'gemini': gemini_status
    })

if __name__ == '__main__':
    print("🚨 Emergency Alert Generator")
    print("=" * 40)
    print("📱 Gemini API configured")
    print("🚀 Starting server on port 8081...")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=8084, debug=True)