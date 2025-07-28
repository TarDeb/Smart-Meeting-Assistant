import streamlit as st
import threading
import time
from datetime import datetime
import os
from audio_recorder import AudioRecorder
from transcription_service import TranscriptionService
from file_manager import FileManager
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Smart Meeting Assistant",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-recording {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .status-ready {
        background-color: #44ff44;
        color: black;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .transcription-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        min-height: 300px;
        max-height: 500px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'recording_state' not in st.session_state:
    st.session_state.recording_state = False
if 'transcription_text' not in st.session_state:
    st.session_state.transcription_text = ""
if 'audio_recorder' not in st.session_state:
    st.session_state.audio_recorder = AudioRecorder()
if 'transcription_service' not in st.session_state:
    st.session_state.transcription_service = TranscriptionService()
if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager()

def start_recording():
    """Start the recording process"""
    st.session_state.recording_state = True
    st.session_state.transcription_text = ""
    
    # Start recording in background thread
    def record_audio():
        try:
            audio_file = st.session_state.audio_recorder.start_recording()
            
            while st.session_state.recording_state:
                time.sleep(1)
                if st.session_state.audio_recorder.has_audio_data():
                    chunk_file = st.session_state.audio_recorder.get_audio_chunk()
                    if chunk_file:
                        text = st.session_state.transcription_service.transcribe_audio(chunk_file)
                        if text:
                            st.session_state.transcription_text += text + "\n"
            
            # Final transcription
            st.session_state.audio_recorder.stop_recording()
            final_text = st.session_state.transcription_service.transcribe_audio(audio_file)
            if final_text:
                st.session_state.transcription_text = final_text
                
        except Exception as e:
            st.error(f"Recording error: {str(e)}")
    
    thread = threading.Thread(target=record_audio)
    thread.daemon = True
    thread.start()

def stop_recording():
    """Stop the recording process"""
    st.session_state.recording_state = False

def main():
    # Header
    st.markdown('<h1 class="main-header">🎤 Smart Meeting Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Recording controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔴 Start Recording", disabled=st.session_state.recording_state):
                start_recording()
                st.rerun()
        
        with col2:
            if st.button("⏹️ Stop Recording", disabled=not st.session_state.recording_state):
                stop_recording()
                st.rerun()
        
        # Status indicator
        if st.session_state.recording_state:
            st.markdown('<div class="status-recording">🔴 RECORDING IN PROGRESS</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-ready">✅ Ready to Record</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Settings
        st.header("🔧 Settings")
        language = st.selectbox("Language", ["en", "es", "fr", "de", "it"], index=0)
        audio_quality = st.slider("Audio Quality", 1, 10, 7)
        
        st.divider()
        
        # File management
        st.header("📁 File Management")
        if st.session_state.transcription_text:
            if st.button("💾 Save Transcription"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"meeting_transcription_{timestamp}.txt"
                success = st.session_state.file_manager.save_transcription(
                    st.session_state.transcription_text, filename
                )
                if success:
                    st.success(f"Saved as {filename}")
                else:
                    st.error("Failed to save transcription")
        
        # Download button
        if st.session_state.transcription_text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            download_content = f"Meeting Transcription\nGenerated: {timestamp}\n{'='*50}\n\n{st.session_state.transcription_text}"
            
            st.download_button(
                label="📥 Download Transcription",
                data=download_content,
                file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        # View saved files
        saved_files = st.session_state.file_manager.get_transcription_files()
        if saved_files:
            st.header("📋 Saved Transcriptions")
            for file_info in saved_files[:5]:  # Show last 5 files
                if st.button(f"📄 {file_info['name']}", key=file_info['path']):
                    content = st.session_state.file_manager.load_transcription(file_info['path'])
                    if content:
                        st.session_state.transcription_text = content
                        st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Live Transcription")
        
        # Auto-refresh transcription display every 2 seconds during recording
        if st.session_state.recording_state:
            time.sleep(2)
            st.rerun()
        
        # Transcription display
        transcription_container = st.container()
        with transcription_container:
            if st.session_state.transcription_text:
                st.markdown(
                    f'<div class="transcription-box">{st.session_state.transcription_text}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("👆 Click 'Start Recording' to begin transcribing your meeting")
        
        # Meeting summary section
        if st.session_state.transcription_text and not st.session_state.recording_state:
            st.header("📊 Meeting Summary")
            
            # Basic analytics
            word_count = len(st.session_state.transcription_text.split())
            char_count = len(st.session_state.transcription_text)
            
            col1_summary, col2_summary, col3_summary = st.columns(3)
            with col1_summary:
                st.metric("Word Count", word_count)
            with col2_summary:
                st.metric("Character Count", char_count)
            with col3_summary:
                estimated_duration = word_count / 150  # Average speaking rate
                st.metric("Estimated Duration", f"{estimated_duration:.1f} min")
    
    with col2:
        st.header("📈 Audio Visualization")
        
        # Audio level visualization (simulated)
        if st.session_state.recording_state:
            # Simulate audio levels
            audio_levels = np.random.random(50) * 100
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=audio_levels,
                mode='lines',
                name='Audio Level',
                line=dict(color='#1f77b4', width=2)
            ))
            fig.update_layout(
                title="Real-time Audio Levels",
                xaxis_title="Time",
                yaxis_title="Level (%)",
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔇 No audio input detected")
        
        # Recording info
        st.header("ℹ️ Session Info")
        if st.session_state.recording_state:
            st.write("🎙️ **Status:** Recording")
            st.write(f"⏱️ **Started:** {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.write("⏸️ **Status:** Stopped")
        
        # Quick tips
        st.header("💡 Tips")
        st.markdown("""
        - Speak clearly and at normal pace
        - Minimize background noise
        - Keep microphone close
        - Take pauses for better transcription
        - Internet connection required for best results
        """)

if __name__ == "__main__":
    main()
