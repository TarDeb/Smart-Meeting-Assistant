"""
Simple test for YouTube system audio recording and transcription
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from enhanced_audio_recorder import EnhancedAudioRecorder
from transcription_service import TranscriptionService
import time

def test_youtube_recording():
    print("=== YouTube System Audio Test ===")
    print("1. Open YouTube and play an English video")
    print("2. Make sure the volume is audible")
    print("3. Press Enter when ready...")
    input()
    
    # Create recorder and transcription service
    recorder = EnhancedAudioRecorder()
    recorder.set_audio_source("system")
    transcription_service = TranscriptionService()
    
    print("Starting 10-second recording of system audio...")
    
    try:
        # Start recording
        recorder.start_recording()
        
        # Record for 10 seconds, checking audio levels
        for i in range(10):
            time.sleep(1)
            level = recorder.get_audio_levels()
            print(f"Second {i+1}: Audio level = {level:.1f}%")
            
            # Try to get a chunk every 2 seconds
            if i > 0 and i % 2 == 0:
                chunk_file = recorder.get_audio_chunk(seconds=2)
                if chunk_file:
                    print(f"  Processing chunk: {os.path.basename(chunk_file)}")
                    text = transcription_service.transcribe_audio(chunk_file)
                    if text:
                        print(f"  ✅ Live transcription: {text}")
                    else:
                        print("  ⚠️  No transcription for this chunk")
        
        # Stop recording and get final result
        recorder.stop_recording()
        
        print("\nRecording completed!")
        
        if recorder.frames:
            print(f"Recorded {len(recorder.frames)} audio frames")
        else:
            print("❌ No audio frames recorded!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_youtube_recording()
    input("Press Enter to exit...")
