#!/usr/bin/env python3
"""
Integrated Voice Transcription + Emergency Alert Server
Combines Whisper transcription with Gemini alert generation
"""

import os
import base64
import tempfile
import json
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import whisper
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
whisper_model = None
gemini_model = None

def load_whisper_model(model_size="base"):
    """Load the Whisper model"""
    global whisper_model
    try:
        logger.info(f"Loading Whisper model: {model_size}")
        whisper_model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        return False

def initialize_gemini():
    """Initialize Gemini model"""
    global gemini_model
    try:
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyD5uLyJo-7vbkMwzVPjPoicbLFzzpuaqcg')
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("Gemini model initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        return False

def generate_emergency_prompt(transcription, location=None):
    """Generate prompt for Gemini to create emergency alert"""
    location_text = f"\nLocation data: {location}" if location else ""
    
    prompt = f"""You are an emergency message processor. A person in danger has sent a voice message that was transcribed (may contain transcription errors).

Your task: Generate a detailed, clear emergency alert message that their emergency contacts will receive via SMS. Include ALL relevant information.

Voice transcription: "{transcription}"{location_text}

Create an emergency alert message that includes:
- 🚨 Clear statement that this is an emergency with emoji
- What is happening (situation/threat)
- Exact location details if mentioned
- Any descriptions of people/vehicles if mentioned  
- Current actions the person is taking
- Sense of urgency and recommended actions for contacts

Make the message detailed and comprehensive. Don't worry about length - include all important details.

Emergency Alert Message:"""
    return prompt

def generate_alert_with_retry(prompt, max_retries=3):
    """Generate content with retry logic for rate limits"""
    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                else:
                    raise Exception("Rate limit exceeded. Please wait a minute and try again.")
            else:
                raise

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'emergency_interface.html')

@app.route('/transcribe-and-alert', methods=['POST'])
def transcribe_and_alert():
    """
    Complete pipeline: Transcribe audio -> Generate emergency alert
    Expects JSON with base64 encoded audio data
    """
    try:
        if whisper_model is None:
            return jsonify({'error': 'Whisper model not loaded'}), 500
        
        if gemini_model is None:
            return jsonify({'error': 'Gemini model not initialized'}), 500
        
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        logger.info("=== Starting transcription and alert generation ===")
        
        # Step 1: Decode and save audio
        try:
            audio_data = base64.b64decode(data['audio'])
            logger.info(f"Decoded audio data size: {len(audio_data)} bytes")
        except Exception as e:
            logger.error(f"Failed to decode base64 audio: {e}")
            return jsonify({
                'error': 'Invalid base64 audio data',
                'success': False
            }), 400
        
        if len(audio_data) < 100:
            logger.warning(f"Audio file too small: {len(audio_data)} bytes")
            return jsonify({
                'error': 'Audio file too small. Please speak for at least 2 seconds.',
                'success': False
            }), 400
        
        audio_format = data.get('format', 'webm')
        file_extension = 'webm' if audio_format == 'webm' else 'wav'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Step 2: Transcribe with Whisper
            logger.info("Step 1/2: Transcribing audio with Whisper...")
            
            try:
                result = whisper_model.transcribe(
                    temp_file_path,
                    fp16=False,
                    language=None,
                    task="transcribe"
                )
            except Exception as transcribe_error:
                logger.warning(f"Direct transcription failed, attempting conversion: {transcribe_error}")
                
                # Fallback: Convert to WAV
                import subprocess
                wav_path = temp_file_path.replace(f'.{file_extension}', '.wav')
                
                subprocess.run([
                    'ffmpeg', '-i', temp_file_path, 
                    '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
                    wav_path, '-y'
                ], check=True, capture_output=True)
                
                result = whisper_model.transcribe(wav_path, fp16=False, language=None, task="transcribe")
                os.unlink(wav_path)
            
            transcription = result['text'].strip()
            language = result.get('language', 'unknown')
            logger.info(f"✓ Transcription completed: '{transcription[:100]}...'")
            
            # Step 3: Generate emergency alert with Gemini
            logger.info("Step 2/2: Generating emergency alert with Gemini...")
            
            location = data.get('location')
            prompt = generate_emergency_prompt(transcription, location)
            
            emergency_message = generate_alert_with_retry(prompt)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            emergency_message = f"{emergency_message}\n\n⏰ Time sent: {timestamp}"
            
            logger.info("✓ Emergency alert generated successfully")
            logger.info("=== Pipeline completed successfully ===")
            
            # Clean up
            os.unlink(temp_file_path)
            
            return jsonify({
                'success': True,
                'transcription': transcription,
                'language': language,
                'alert_message': emergency_message,
                'timestamp': timestamp
            })
            
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    whisper_status = "loaded" if whisper_model is not None else "not loaded"
    
    gemini_status = "not loaded"
    if gemini_model is not None:
        try:
            test_response = gemini_model.generate_content("Test")
            gemini_status = "connected"
        except:
            gemini_status = "error"
    
    return jsonify({
        'status': 'healthy',
        'whisper_model': whisper_status,
        'gemini_model': gemini_status
    })

if __name__ == '__main__':
    print("🚨 Integrated Emergency Alert System")
    print("=" * 50)
    
    # Load Whisper model
    print("📝 Loading Whisper model...")
    if load_whisper_model("base"):
        print("✅ Whisper model loaded successfully")
    else:
        print("❌ Failed to load Whisper model")
        exit(1)
    
    # Initialize Gemini
    print("🤖 Initializing Gemini...")
    if initialize_gemini():
        print("✅ Gemini initialized successfully")
    else:
        print("❌ Failed to initialize Gemini")
        exit(1)
    
    print("\n🚀 Starting integrated server...")
    print("📱 Open http://localhost:8080 in your browser")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=True)