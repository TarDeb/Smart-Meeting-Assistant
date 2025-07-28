import sounddevice as sd
import wave
import threading
import time
import os
import numpy as np
from datetime import datetime
from scipy.io.wavfile import write

class EnhancedAudioRecorder:
    def __init__(self):
        self.chunk = 1024
        self.channels = 2  # Stereo for better system audio capture
        self.rate = 44100
        self.recording = False
        self.frames = []
        self.recording_thread = None
        self.audio_source = "microphone"  # "microphone", "system", or "both"
        
    def set_audio_source(self, source):
        """Set the audio source: 'microphone', 'system', or 'both'"""
        if source in ["microphone", "system", "both"]:
            self.audio_source = source
        else:
            raise ValueError("Audio source must be 'microphone', 'system', or 'both'")
    
    def get_available_devices(self):
        """Get list of available audio devices"""
        devices = sd.query_devices()
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            device_info = {
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'] if device['max_input_channels'] > 0 else device['max_output_channels'],
                'default_samplerate': device['default_samplerate']
            }
            
            if device['max_input_channels'] > 0:
                input_devices.append(device_info)
            if device['max_output_channels'] > 0:
                output_devices.append(device_info)
        
        return {
            'input_devices': input_devices,
            'output_devices': output_devices,
            'default_input': sd.default.device[0],
            'default_output': sd.default.device[1]
        }
    
    def start_recording(self):
        """Start recording audio based on selected source"""
        self.recording = True
        self.frames = []
        
        try:
            if self.audio_source == "microphone":
                self._start_microphone_recording()
            elif self.audio_source == "system":
                self._start_system_recording()
            elif self.audio_source == "both":
                self._start_mixed_recording()
            
            return self._get_temp_filename()
            
        except Exception as e:
            raise Exception(f"Failed to start recording: {str(e)}")
    
    def _start_microphone_recording(self):
        """Start recording from microphone"""
        def audio_callback(indata, frames, time, status):
            if self.recording and status.input_underflow == False:
                self.frames.append(indata.copy())
        
        try:
            # Use the default microphone device
            self.stream = sd.InputStream(
                samplerate=self.rate,
                channels=1,  # Mono for microphone
                callback=audio_callback,
                blocksize=self.chunk,
                dtype=np.float32
            )
            self.stream.start()
            print("Started microphone recording")
        except Exception as e:
            print(f"Failed to start microphone recording: {e}")
            raise
    
    def _start_system_recording(self):
        """Start recording system audio using Stereo Mix or WASAPI loopback"""
        try:
            # First, try to find Stereo Mix device
            stereo_mix_device = self.find_stereo_mix_device()
            
            def audio_callback(indata, frames, time, status):
                if self.recording:
                    self.frames.append(indata.copy())
            
            if stereo_mix_device is not None:
                print(f"Using Stereo Mix device: {stereo_mix_device}")
                # Use Stereo Mix for system audio recording
                self.stream = sd.InputStream(
                    device=stereo_mix_device,
                    samplerate=self.rate,
                    channels=2,  # Stereo for system audio
                    callback=audio_callback,
                    blocksize=self.chunk,
                    dtype=np.float32
                )
                self.stream.start()
            else:
                # Try WASAPI loopback approach
                print("Stereo Mix not found, trying WASAPI loopback...")
                self._try_wasapi_loopback(audio_callback)
                
        except Exception as e:
            raise Exception(f"Failed to start system recording: {str(e)}")
    
    def find_stereo_mix_device(self):
        """Find Stereo Mix or similar device for system audio recording"""
        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                # Look for stereo mix, wave out mix, what u hear, loopback
                if any(keyword in device_name for keyword in ['stereo', 'stereomix', 'wave out mix', 'what u hear', 'loopback']):
                    if device['max_input_channels'] > 0:
                        print(f"Found stereo mix device: {device['name']} (ID: {i})")
                        return i
            return None
        except:
            return None
    
    def _try_wasapi_loopback(self, audio_callback):
        """Try to use WASAPI loopback for system audio recording"""
        try:
            # Try to find WASAPI devices
            devices = sd.query_devices()
            wasapi_devices = []
            
            for i, device in enumerate(devices):
                if 'wasapi' in device['name'].lower() and device['max_input_channels'] > 0:
                    wasapi_devices.append(i)
            
            if wasapi_devices:
                # Try the first WASAPI input device
                device_id = wasapi_devices[0]
                print(f"Using WASAPI device: {device_id}")
                self.stream = sd.InputStream(
                    device=device_id,
                    samplerate=self.rate,
                    channels=2,
                    callback=audio_callback,
                    blocksize=self.chunk,
                    dtype=np.float32
                )
                self.stream.start()
            else:
                raise Exception("No WASAPI devices available")
                
        except Exception as e:
            # Final fallback: use default input and inform user
            print(f"Warning: System audio loopback not available ({e}). Using default input device.")
            print("To record system audio, please enable 'Stereo Mix' in your sound settings.")
            
            self.stream = sd.InputStream(
                samplerate=self.rate,
                channels=1,  # Use mono for fallback
                callback=audio_callback,
                blocksize=self.chunk,
                dtype=np.float32
            )
            self.stream.start()
    
    def _start_mixed_recording(self):
        """Start recording both microphone and system audio"""
        # This is complex and would require mixing two streams
        # For simplicity, we'll use system recording which often captures both
        self._start_system_recording()
    
    def stop_recording(self):
        """Stop recording and save audio file"""
        self.recording = False
        
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
        
        # Save the recorded audio
        filename = self._get_temp_filename()
        self._save_audio_file(filename)
        return filename
    
    def has_audio_data(self):
        """Check if there's audio data available"""
        return len(self.frames) > 10
    
    def get_audio_chunk(self, seconds=1):
        """Get a chunk of audio for real-time processing (default: 1 second)"""
        num_frames = int(self.rate * seconds / self.chunk)
        if len(self.frames) >= num_frames:
            chunk_frames = self.frames[:num_frames]
            # Remove the frames that have been processed
            self.frames = self.frames[num_frames:]
            chunk_filename = self._get_temp_filename("chunk")
            self._save_audio_file(chunk_filename, chunk_frames)
            return chunk_filename
        return None
    
    def get_audio_levels(self):
        """Get current audio levels for visualization"""
        if self.frames:
            recent_frames = self.frames[-5:] if len(self.frames) >= 5 else self.frames
            if recent_frames:
                audio_data = np.concatenate(recent_frames)
                return np.abs(audio_data).mean() * 100
        return 0
    
    def _save_audio_file(self, filename, frames=None):
        """Save audio frames to file"""
        if frames is None:
            frames = self.frames
            
        if not frames:
            raise Exception("No audio data to save")
        
        try:
            # Concatenate all frames
            audio_data = np.concatenate(frames)
            
            # Ensure the data is in the right format for speech recognition
            if audio_data.dtype != np.int16:
                # Convert float32 to int16 with proper scaling
                audio_data = np.clip(audio_data * 32767, -32767, 32767).astype(np.int16)
            
            # Save using wave module for better compatibility
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1 if len(audio_data.shape) == 1 else audio_data.shape[1])
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.rate)
                wf.writeframes(audio_data.tobytes())
            
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
        if hasattr(self, 'stream') and self.stream:
            self.stream.close()
        
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

    def test_system_audio_capture(self):
        """Test system audio capture capability"""
        try:
            devices = self.get_available_devices()
            print("Available audio devices:")
            print("\nInput devices:")
            for device in devices['input_devices']:
                print(f"  {device['id']}: {device['name']} ({device['channels']} channels)")
            
            print("\nOutput devices:")
            for device in devices['output_devices']:
                print(f"  {device['id']}: {device['name']} ({device['channels']} channels)")
            
            print(f"\nDefault input: {devices['default_input']}")
            print(f"Default output: {devices['default_output']}")
            
            return True
        except Exception as e:
            print(f"Error testing audio devices: {e}")
            return False
