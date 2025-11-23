#!/usr/bin/env python3
"""
Voice Transcription Server using OpenAI Whisper
Handles audio file transcription from the web interface
"""

import os
import base64
import tempfile
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import whisper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store the Whisper model
whisper_model = None

def load_whisper_model(model_size="base"):
    """Load the Whisper model. Options: tiny, base, small, medium, large"""
    global whisper_model
    try:
        logger.info(f"Loading Whisper model: {model_size}")
        whisper_model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        return False

@app.route('/')
def serve_index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio using Whisper model
    Expects JSON with base64 encoded audio data
    """
    try:
        if whisper_model is None:
            return jsonify({'error': 'Whisper model not loaded'}), 500
        
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        logger.info(f"Received transcription request with audio format: {data.get('format', 'unknown')}")
        
        # Decode base64 audio
        try:
            audio_data = base64.b64decode(data['audio'])
            logger.info(f"Decoded audio data size: {len(audio_data)} bytes")
        except Exception as e:
            logger.error(f"Failed to decode base64 audio: {e}")
            return jsonify({
                'error': 'Invalid base64 audio data',
                'success': False
            }), 400
        
        audio_format = data.get('format', 'webm')
        
        # Create temporary file with proper extension
        file_extension = 'webm' if audio_format == 'webm' else 'wav'
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        # If the file is very small, it might be corrupted
        if len(audio_data) < 100:  # Less than 100 bytes
            os.unlink(temp_file_path)
            logger.warning(f"Audio file too small: {len(audio_data)} bytes")
            return jsonify({
                'error': 'Audio file too small or corrupted. Please try recording again.',
                'success': False
            }), 400
        
        try:
            # Transcribe using Whisper
            logger.info(f"Starting transcription of file: {temp_file_path} (size: {len(audio_data)} bytes)")
            
            try:
                # First attempt: transcribe directly
                result = whisper_model.transcribe(
                    temp_file_path,
                    fp16=False,  # Use FP32 for better compatibility
                    language=None,  # Auto-detect language
                    task="transcribe"
                )
            except Exception as transcribe_error:
                logger.warning(f"Direct transcription failed: {transcribe_error}")
                logger.info("Attempting to convert audio format...")
                
                # Fallback: try to convert to WAV using FFmpeg
                import subprocess
                wav_path = temp_file_path.replace(f'.{file_extension}', '.wav')
                
                try:
                    # Convert to WAV format
                    subprocess.run([
                        'ffmpeg', '-i', temp_file_path, 
                        '-ar', '16000',  # 16kHz sample rate
                        '-ac', '1',      # Mono
                        '-c:a', 'pcm_s16le',  # PCM 16-bit
                        wav_path, '-y'   # Overwrite if exists
                    ], check=True, capture_output=True)
                    
                    # Try transcription with converted file
                    result = whisper_model.transcribe(
                        wav_path,
                        fp16=False,
                        language=None,
                        task="transcribe"
                    )
                    
                    # Clean up converted file
                    os.unlink(wav_path)
                    
                except subprocess.CalledProcessError as conv_error:
                    logger.error(f"Audio conversion failed: {conv_error}")
                    raise transcribe_error  # Re-raise original error
                except Exception as wav_error:
                    logger.error(f"WAV transcription failed: {wav_error}")
                    if os.path.exists(wav_path):
                        os.unlink(wav_path)
                    raise transcribe_error  # Re-raise original error
            
            transcription = result['text'].strip()
            logger.info(f"Transcription completed: {transcription[:50]}...")
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return jsonify({
                'text': transcription,
                'language': result.get('language', 'unknown'),
                'success': True
            })
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    model_status = "loaded" if whisper_model is not None else "not loaded"
    return jsonify({
        'status': 'healthy',
        'whisper_model': model_status
    })

@app.route('/model/reload', methods=['POST'])
def reload_model():
    """Reload the Whisper model with a different size"""
    data = request.get_json()
    model_size = data.get('model_size', 'base') if data else 'base'
    
    valid_sizes = ['tiny', 'base', 'small', 'medium', 'large']
    if model_size not in valid_sizes:
        return jsonify({
            'error': f'Invalid model size. Choose from: {valid_sizes}'
        }), 400
    
    success = load_whisper_model(model_size)
    if success:
        return jsonify({
            'message': f'Whisper model "{model_size}" loaded successfully',
            'model_size': model_size
        })
    else:
        return jsonify({
            'error': f'Failed to load Whisper model "{model_size}"'
        }), 500

if __name__ == '__main__':
    print("🎤 Voice Transcription Server")
    print("=" * 40)
    
    # Load the Whisper model on startup
    print("Loading Whisper model...")
    if load_whisper_model("base"):
        print("✅ Whisper model loaded successfully")
    else:
        print("❌ Failed to load Whisper model")
        print("Make sure you have installed: pip install openai-whisper")
        exit(1)
    
    print("\n🚀 Starting server...")
    print("📱 Open http://localhost:8080 in your browser")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=8080, debug=True)