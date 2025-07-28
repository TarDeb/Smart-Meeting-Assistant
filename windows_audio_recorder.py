import sounddevice as sd
import wave
import threading
import time
import os
import numpy as np
from datetime import datetime
from scipy.io.wavfile import write
import subprocess
import sys

class WindowsAudioRecorder:
    def __init__(self):
        self.chunk = 1024
        self.channels = 2  # Stereo for better system audio capture
        self.rate = 44100
        self.recording = False
        self.frames = []
        self.recording_thread = None
        self.audio_source = "microphone"  # "microphone", "system", or "both"
        self.stream = None
        
    def set_audio_source(self, source):
        """Set the audio source: 'microphone', 'system', or 'both'"""
        if source in ["microphone", "system", "both"]:
            self.audio_source = source
        else:
            raise ValueError("Audio source must be 'microphone', 'system', or 'both'")
    
    def get_available_devices(self):
        """Get list of available audio devices"""
        try:
            devices = sd.query_devices()
            input_devices = []
            output_devices = []
            
            for i, device in enumerate(devices):
                device_info = {
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'] if device['max_input_channels'] > 0 else device['max_output_channels'],
                    'default_samplerate': device['default_samplerate'],
                    'hostapi': device['hostapi']
                }
                
                if device['max_input_channels'] > 0:
                    input_devices.append(device_info)
                if device['max_output_channels'] > 0:
                    output_devices.append(device_info)
            
            return {
                'input_devices': input_devices,
                'output_devices': output_devices,
                'default_input': sd.default.device[0] if sd.default.device[0] is not None else 0,
                'default_output': sd.default.device[1] if sd.default.device[1] is not None else 0
            }
        except Exception as e:
            print(f"Error getting devices: {e}")
            return {'input_devices': [], 'output_devices': [], 'default_input': 0, 'default_output': 0}
    
    def find_stereo_mix_device(self):
        """Try to find Stereo Mix or similar device for system audio recording"""
        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                # Look for stereo mix, wave out mix, what u hear, loopback devices
                if any(keyword in device_name for keyword in ['stereo', 'stereomix', 'wave out mix', 'what u hear', 'loopback']):
                    if device['max_input_channels'] > 0:
                        print(f"Found stereo mix device: {device['name']} (ID: {i})")
                        return i
            return None
        except:
            return None
    
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
            self.stream = sd.InputStream(
                samplerate=self.rate,
                channels=1,  # Mono for microphone
                callback=audio_callback,
                blocksize=self.chunk,
                dtype=np.float32
            )
            self.stream.start()
        except Exception as e:
            raise Exception(f"Failed to start microphone recording: {str(e)}")
    
    def _start_system_recording(self):
        """Start recording system audio"""
        try:
            # First, try to find Stereo Mix device
            stereo_mix_device = self.find_stereo_mix_device()
            
            def audio_callback(indata, frames, time, status):
                if self.recording and status.input_underflow == False:
                    self.frames.append(indata.copy())
            
            if stereo_mix_device is not None:
                # Use Stereo Mix device
                print(f"Using Stereo Mix device: {stereo_mix_device}")
                self.stream = sd.InputStream(
                    device=stereo_mix_device,
                    samplerate=self.rate,
                    channels=2,
                    callback=audio_callback,
                    blocksize=self.chunk,
                    dtype=np.float32
                )
                self.stream.start()
            else:
                # Try WASAPI loopback approach
                self._try_wasapi_loopback(audio_callback)
                
        except Exception as e:
            raise Exception(f"Failed to start system recording: {str(e)}")
    
    def _try_wasapi_loopback(self, audio_callback):
        """Try to use WASAPI loopback for system audio recording"""
        try:
            # Try to find WASAPI host API
            host_apis = sd.query_hostapis()
            wasapi_id = None
            
            for i, api in enumerate(host_apis):
                if 'wasapi' in api['name'].lower():
                    wasapi_id = i
                    break
            
            if wasapi_id is not None:
                # Get default output device for WASAPI
                devices = sd.query_devices()
                default_output = sd.default.device[1]
                
                # Try to use output device as input (loopback)
                self.stream = sd.InputStream(
                    device=default_output,
                    samplerate=self.rate,
                    channels=2,
                    callback=audio_callback,
                    blocksize=self.chunk,
                    dtype=np.float32
                )
                self.stream.start()
                print("Using WASAPI loopback recording")
            else:
                raise Exception("WASAPI not available")
                
        except Exception as e:
            # Final fallback: use default input and inform user
            print(f"Warning: System audio loopback not available ({e}). Using default input device.")
            print("To record system audio, please enable 'Stereo Mix' in your sound settings.")
            
            self.stream = sd.InputStream(
                samplerate=self.rate,
                channels=2,
                callback=audio_callback,
                blocksize=self.chunk,
                dtype=np.float32
            )
            self.stream.start()
    
    def _start_mixed_recording(self):
        """Start recording both microphone and system audio"""
        # For simplicity, we'll use system recording which may capture both
        # A full implementation would require mixing two separate streams
        print("Mixed recording: Using system audio recording (may include microphone if enabled in system)")
        self._start_system_recording()
    
    def stop_recording(self):
        """Stop recording and save audio file"""
        self.recording = False
        
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            finally:
                self.stream = None
        
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
            
            # Ensure the data is in the right format
            if audio_data.dtype != np.int16:
                # Convert float32 to int16
                audio_data = np.clip(audio_data * 32767, -32767, 32767).astype(np.int16)
            
            # Save using scipy
            write(filename, self.rate, audio_data)
            
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
            try:
                self.stream.close()
            except:
                pass
        
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

    def test_audio_setup(self):
        """Test and display audio setup information"""
        try:
            print("=== Audio Setup Test ===")
            devices = self.get_available_devices()
            
            print("\nAvailable Input Devices:")
            for device in devices['input_devices']:
                print(f"  ID {device['id']}: {device['name']} ({device['channels']} channels)")
            
            print("\nAvailable Output Devices:")
            for device in devices['output_devices']:
                print(f"  ID {device['id']}: {device['name']} ({device['channels']} channels)")
            
            stereo_mix = self.find_stereo_mix_device()
            if stereo_mix:
                print(f"\n✓ Stereo Mix device found: ID {stereo_mix}")
                print("  System audio recording should work well!")
            else:
                print("\n⚠ No Stereo Mix device found.")
                print("  To enable system audio recording:")
                print("  1. Right-click on speaker icon in system tray")
                print("  2. Select 'Open Sound settings'")
                print("  3. Click 'Sound Control Panel'")
                print("  4. Go to 'Recording' tab")
                print("  5. Right-click in empty area and check 'Show Disabled Devices'")
                print("  6. Enable 'Stereo Mix' if available")
            
            return True
        except Exception as e:
            print(f"Error testing audio setup: {e}")
            return False

    def enable_stereo_mix_instructions(self):
        """Provide instructions for enabling Stereo Mix"""
        instructions = """
        To record system audio (like YouTube videos), you need to enable Stereo Mix:
        
        1. Right-click the speaker icon in your system tray (bottom-right corner)
        2. Select "Open Sound settings"
        3. Scroll down and click "Sound Control Panel" 
        4. Go to the "Recording" tab
        5. Right-click in an empty area and check "Show Disabled Devices"
        6. Look for "Stereo Mix" or "Wave Out Mix"
        7. Right-click on it and select "Enable"
        8. Right-click again and select "Set as Default Device"
        9. Click "OK" to close the dialog
        
        If Stereo Mix is not available, your sound card may not support it.
        In that case, you can try using virtual audio cable software.
        """
        return instructions
