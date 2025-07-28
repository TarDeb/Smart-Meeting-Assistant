import pyaudio
import wave
import threading
import time
import os
from datetime import datetime
import streamlit as st

class AudioRecorder:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    @st.cache_resource
    def _initialize_audio(_self):
        """Initialize audio system (cached for Streamlit)"""
        try:
            return pyaudio.PyAudio()
        except Exception as e:
            st.error(f"Failed to initialize audio: {str(e)}")
            return None
        
    def start_recording(self):
        """Start recording audio"""
        self.recording = True
        self.frames = []
        
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                stream_callback=self._audio_callback
            )
            
            self.stream.start_stream()
            return self._get_temp_filename()
            
        except Exception as e:
            st.error(f"Failed to start recording: {str(e)}")
            raise Exception(f"Failed to start recording: {str(e)}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.recording:
            self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def stop_recording(self):
        """Stop recording and save audio file"""
        self.recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        # Save the recorded audio
        filename = self._get_temp_filename()
        self._save_audio_file(filename)
        return filename
    
    def has_audio_data(self):
        """Check if there's audio data available"""
        return len(self.frames) > 10
    
    def get_audio_chunk(self):
        """Get a chunk of audio for real-time processing"""
        if len(self.frames) > 20:  # Process every 20 chunks for real-time
            chunk_frames = self.frames[-20:]
            chunk_filename = self._get_temp_filename("chunk")
            self._save_audio_file(chunk_filename, chunk_frames)
            return chunk_filename
        return None
    
    def get_audio_levels(self):
        """Get current audio levels for visualization"""
        if self.frames:
            import numpy as np
            recent_frames = self.frames[-5:] if len(self.frames) >= 5 else self.frames
            audio_data = b''.join(recent_frames)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            return np.abs(audio_array).mean() / 32768.0 * 100
        return 0
    
    def _save_audio_file(self, filename, frames=None):
        """Save audio frames to file"""
        if frames is None:
            frames = self.frames
            
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
        except Exception as e:
            raise Exception(f"Failed to save audio file: {str(e)}")
    
    def _get_temp_filename(self, prefix="recording"):
        """Generate a temporary filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        return os.path.join(temp_dir, f"{prefix}_{timestamp}.wav")
    
    def cleanup(self):
        """Clean up resources"""
        self.recording = False
        if self.stream:
            self.stream.close()
        self.audio.terminate()
        
        # Clean up temp files
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                try:
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except:
                    pass
