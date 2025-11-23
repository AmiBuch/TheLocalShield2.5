# Voice Transcription with OpenAI Whisper

A web-based voice transcription application that records audio for 30 seconds and transcribes it using OpenAI's local Whisper model.

## Features

- 🎙️ **30-second audio recording** with visual timer
- 🎯 **Real-time transcription** using OpenAI Whisper
- 🎨 **Modern, responsive UI** with glassmorphism design
- 🔊 **Audio playback** of recorded clips
- 🌐 **Multiple language support** (auto-detected by Whisper)
- 📱 **Cross-platform compatibility** (works on desktop and mobile)

## Setup Instructions

### 1. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Run the Flask server
python server.py
```

The server will:
- Load the Whisper model (this may take a moment on first run)
- Start on `http://localhost:5000`
- Serve the web interface automatically

### 3. Open the Web Interface

Navigate to `http://localhost:5000` in your web browser.

## Usage

1. **Click the microphone button** to start recording
2. **Speak clearly** for up to 30 seconds (auto-stops at 30s)
3. **Click stop** or wait for auto-stop
4. **View transcription** appears automatically below
5. **Play back** your recording using the audio controls

## Technical Details

### Frontend (index.html)
- Pure JavaScript with Web Audio API
- Records in WebM format with Opus codec
- Responsive design with CSS animations
- Real-time timer and visual feedback

### Backend (server.py)
- Flask web server with CORS support
- OpenAI Whisper integration
- Base64 audio processing
- Temporary file handling for transcription

### Audio Formats Supported
- **Recording**: WebM with Opus codec (browser native)
- **Processing**: Automatic conversion by Whisper
- **Playback**: WebM audio in browser

## Configuration

### Whisper Model Sizes
You can change the Whisper model size by modifying `server.py`:

- `tiny` - Fastest, least accurate (~39 MB)
- `base` - Good balance (default) (~74 MB)
- `small` - Better accuracy (~244 MB)
- `medium` - High accuracy (~769 MB)
- `large` - Best accuracy (~1550 MB)

### API Endpoints

- `GET /` - Serve the web interface
- `POST /transcribe` - Transcribe audio data
- `GET /health` - Health check
- `POST /model/reload` - Reload Whisper model

## Troubleshooting

### Common Issues

1. **Microphone not working**
   - Check browser permissions
   - Ensure HTTPS or localhost access
   - Try refreshing the page

2. **Transcription fails**
   - Ensure server is running
   - Check console for error messages
   - Verify Whisper model loaded successfully

3. **Poor transcription quality**
   - Speak clearly and close to microphone
   - Reduce background noise
   - Consider upgrading to larger Whisper model

### Browser Compatibility

- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari (macOS/iOS)
- ✅ Edge

## Next Steps

- 🔌 **WebSocket integration** for real-time streaming
- 📊 **Audio visualization** during recording
- 💾 **Save transcriptions** to file
- 🌍 **Multi-language UI** support
- 🎛️ **Audio settings** (quality, format options)

## Dependencies

- **Flask** - Web server framework
- **OpenAI Whisper** - Speech-to-text model
- **PyTorch** - Machine learning backend
- **Flask-CORS** - Cross-origin resource sharing

## License

This project is open source and available under the MIT License.
