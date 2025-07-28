"""
Simple test script to verify audio recording works
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_audio_recorder import EnhancedAudioRecorder
import time

def test_microphone():
    print("=== Testing Microphone Recording ===")
    recorder = EnhancedAudioRecorder()
    recorder.set_audio_source("microphone")
    
    print("Starting 5-second microphone test...")
    print("Please speak into your microphone...")
    
    try:
        filename = recorder.start_recording()
        
        for i in range(5):
            time.sleep(1)
            level = recorder.get_audio_levels()
            print(f"Second {i+1}: Audio level = {level:.1f}%")
        
        recorder.stop_recording()
        print(f"✅ Microphone test completed! Audio saved to: {filename}")
        
        if recorder.frames:
            print(f"Recorded {len(recorder.frames)} audio frames")
        else:
            print("❌ No audio frames recorded!")
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")

def test_system_audio():
    print("\n=== Testing System Audio Recording ===")
    recorder = EnhancedAudioRecorder()
    recorder.set_audio_source("system")
    
    print("Starting 5-second system audio test...")
    print("Please play some audio (YouTube, music, etc.)...")
    input("Press Enter when audio is playing...")
    
    try:
        filename = recorder.start_recording()
        
        for i in range(5):
            time.sleep(1)
            level = recorder.get_audio_levels()
            print(f"Second {i+1}: Audio level = {level:.1f}%")
        
        recorder.stop_recording()
        print(f"✅ System audio test completed! Audio saved to: {filename}")
        
        if recorder.frames:
            print(f"Recorded {len(recorder.frames)} audio frames")
        else:
            print("❌ No audio frames recorded!")
            
    except Exception as e:
        print(f"❌ System audio test failed: {e}")

if __name__ == "__main__":
    print("Audio Recording Test")
    print("=" * 30)
    
    # Test microphone first
    test_microphone()
    
    # Test system audio
    choice = input("\nTest system audio recording? (y/n): ").lower()
    if choice == 'y':
        test_system_audio()
    
    print("\nTest completed!")
    input("Press Enter to exit...")
