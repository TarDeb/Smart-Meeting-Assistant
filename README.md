<<<<<<< HEAD
# Smart Meeting Assistant

A comprehensive Python application that records meetings and provides **real-time transcription** with both desktop GUI and system audio recording capabilities.

## ✨ Features

### 🎤 Audio Recording
- **Microphone recording** - Record your voice and conversations
- **System audio recording** - Capture YouTube videos, online meetings, music, or any system audio
- **Both simultaneously** - Record microphone + system audio together
- **Real-time audio level monitoring** - Visual feedback with live audio level bar

### 🎯 Live Transcription
- **Real-time speech-to-text** - See transcription appear as you speak (every 1-2 seconds)
- **Google Speech Recognition** - High-quality online transcription
- **Offline fallback** - PocketSphinx for when internet is unavailable
- **Multiple audio sources** - Works with microphone, system audio, or both

### 💻 User Interface
- **Modern desktop GUI** - Built with tkinter for native Windows experience
- **Audio source selection** - Easy radio buttons to choose recording source
- **Live transcription display** - Real-time text updates in scrollable window
- **Audio level visualization** - Green progress bar shows recording activity

### 📁 File Management
- **Save transcriptions** - Export to text files with timestamps
- **Automatic cleanup** - Remove temporary audio files and cache
- **Organized storage** - Proper file structure with temp folder management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Windows 10/11 (for system audio recording)
- Internet connection (for Google Speech Recognition)

### Installation

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/TarDeb/Smart-Meeting-Assistant.git
cd Smart-Meeting-Assistant
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Enable Stereo Mix (for system audio recording)**
   - Right-click speaker icon in system tray
   - Select "Open Sound settings"
   - Click "Sound Control Panel"
   - Go to "Recording" tab
   - Right-click and check "Show Disabled Devices"
   - Enable "Stereo Mix" if available

### Usage

#### Desktop Application (Recommended)
```bash
python main.py
```

#### Test Audio Setup
```bash
python test_audio.py
```

## 🎯 How to Use

### For YouTube/System Audio Recording:
1. **Launch the app**: `python main.py`
2. **Select "System Audio (YouTube, etc.)"**
3. **Open YouTube** and play any video
4. **Click "Start Recording"**
5. **Watch live transcription** appear as the video plays!

### For Microphone Recording:
1. **Select "Microphone Only"**
2. **Click "Start Recording"**
3. **Speak clearly** and see real-time transcription

### For Both:
1. **Select "Both (Mic + System)"**
2. **Record conversations while system audio plays**

## 🛠️ Technical Details

### Audio Recording Engines
- **Enhanced Audio Recorder** - Main recording engine with Stereo Mix support
- **Windows Audio Recorder** - Alternative with WASAPI loopback
- **Sounddevice + NumPy** - Professional audio processing

### Transcription Services
- **Google Speech Recognition** - Primary online service
- **PocketSphinx** - Offline fallback option
- **Real-time chunking** - 1-second audio segments for live transcription

### Supported Formats
- **Input**: System audio, microphone, or both
- **Output**: WAV files, text transcriptions with timestamps
- **Languages**: English (primary), with multi-language support

## 📋 Requirements
2. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. For Windows users, you may need to install PyAudio separately:
    ```bash
    pip install pipwin
    pipwin install pyaudio
    ```

## Usage

1. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. Open your web browser and navigate to `http://localhost:8501`
3. Click "Start Recording" to begin capturing audio
4. Watch real-time transcription appear in the browser
5. Click "Stop Recording" when finished
6. Download or save the transcription directly from the web interface

## File Structure

- `app.py` - Main Streamlit application
- `audio_recorder.py` - Audio recording functionality
- `transcription_service.py` - Speech-to-text processing
- `file_manager.py` - File operations for saving/loading
- `components/` - Streamlit custom components
- `static/` - CSS and JavaScript files
- `temp/` - Temporary audio files (auto-created)
- `transcriptions/` - Saved transcription files (auto-created)

## Testing

The Streamlit interface provides an intuitive web-based testing environment:
- Real-time audio visualization
- Live transcription updates
- Interactive file management
- Download transcriptions directly
- Test different audio sources
- Monitor recording status with visual indicators

## Requirements

- Python 3.7+
- Microphone access (browser permissions required)
- Internet connection (for Google Speech Recognition)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Audio drivers compatible with PyAudio

## Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Cloud Deployment
The application can be easily deployed to:
- Streamlit Cloud (streamlit.io)
- Heroku
- AWS/GCP/Azure
- Docker containers

### Sharing
Share your application by:
1. Deploying to Streamlit Cloud for free
2. Using ngrok for temporary public access
3. Setting up reverse proxy for production

## Troubleshooting

1. **Microphone not detected**: 
   - Grant browser microphone permissions
   - Check system audio settings
   - Ensure HTTPS for production deployment

2. **Transcription not working**: 
   - Verify internet connection for Google Speech API
   - Check API quotas and limits
   - Test offline mode with PocketSphinx

3. **Streamlit issues**:
   - Clear browser cache
   - Restart the Streamlit server
   - Check firewall and port settings

4. **Audio quality issues**: 
   - Adjust microphone sensitivity
   - Reduce background noise
   - Test different audio input devices

## Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 11+
- ✅ Edge 79+
- ⚠️ Internet Explorer (not supported)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Open browser to http://localhost:8501
```

## Features Demo

The Streamlit interface includes:
- **Real-time transcription** with live updates
- **Audio visualization** showing recording levels
- **Session management** with save/load functionality
- **Download capabilities** for easy file sharing
- **Responsive design** that adapts to screen size
- **Interactive controls** with immediate feedback
=======
# Smart-Meeting-Assistant
Requirements &amp; Planning


Project Roadmap
--
Smart-Meeting-Assistant
Project Description
The Smart-Meeting-Assistant is an AI-powered tool designed to assist in meetings by transcribing, summarizing, and analyzing conversations in real time. It leverages FastAPI for API endpoints, Vosk for speech recognition, OpenAI for NLP tasks, and spaCy for additional text processing
>>>>>>> 3bac854e4f4370cb0e196d3fab9eaac203402b44
