"""
Audio Setup Test Script
This script helps test and configure audio recording for the Smart Meeting Assistant
"""
import sys
import os

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(__file__))

from windows_audio_recorder import WindowsAudioRecorder
import time

def main():
    print("=== Smart Meeting Assistant Audio Setup Test ===\n")
    
    recorder = WindowsAudioRecorder()
    
    # Test audio setup
    print("Testing audio device configuration...")
    test_success = recorder.test_audio_setup()
    
    if not test_success:
        print("\n❌ Audio setup test failed. Please check your audio drivers.")
        return
    
    print("\n" + "="*50)
    print("SYSTEM AUDIO RECORDING TEST")
    print("="*50)
    
    # Check for Stereo Mix
    stereo_mix = recorder.find_stereo_mix_device()
    if stereo_mix:
        print(f"✅ Stereo Mix device found! (Device ID: {stereo_mix})")
        print("You should be able to record system audio (YouTube, etc.)")
    else:
        print("⚠️  No Stereo Mix device found.")
        print("\nTo record system audio, you need to enable Stereo Mix:")
        print(recorder.enable_stereo_mix_instructions())
    
    print("\n" + "="*50)
    print("QUICK RECORDING TEST")
    print("="*50)
    
    # Test recording
    while True:
        test_type = input("\nWhat would you like to test?\n1. Microphone\n2. System Audio\n3. Exit\nChoice (1-3): ").strip()
        
        if test_type == "3":
            break
        elif test_type == "1":
            test_microphone_recording(recorder)
        elif test_type == "2":
            test_system_recording(recorder)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def test_microphone_recording(recorder):
    """Test microphone recording"""
    print("\n--- Microphone Recording Test ---")
    recorder.set_audio_source("microphone")
    
    input("Press Enter to start 5-second microphone test...")
    try:
        print("Recording from microphone for 5 seconds...")
        filename = recorder.start_recording()
        
        for i in range(5):
            time.sleep(1)
            level = recorder.get_audio_levels()
            print(f"Audio level: {level:.1f}%")
        
        recorder.stop_recording()
        print(f"✅ Microphone test completed! File saved as: {filename}")
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")

def test_system_recording(recorder):
    """Test system audio recording"""
    print("\n--- System Audio Recording Test ---")
    recorder.set_audio_source("system")
    
    stereo_mix = recorder.find_stereo_mix_device()
    if not stereo_mix:
        print("⚠️  Warning: No Stereo Mix device found.")
        print("System audio recording may not work properly.")
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            return
    
    print("Open YouTube or play some music, then press Enter to start recording...")
    input("Press Enter when audio is playing...")
    
    try:
        print("Recording system audio for 5 seconds...")
        filename = recorder.start_recording()
        
        for i in range(5):
            time.sleep(1)
            level = recorder.get_audio_levels()
            print(f"Audio level: {level:.1f}%")
        
        recorder.stop_recording()
        print(f"✅ System audio test completed! File saved as: {filename}")
        
        if stereo_mix:
            print("If you heard the audio you were playing, system recording works!")
        else:
            print("Check the recorded file to see if system audio was captured.")
        
    except Exception as e:
        print(f"❌ System audio test failed: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    print("\nTest completed. You can now run the main application!")
    input("Press Enter to exit...")
