"""
Test transcription service with recorded audio files
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from transcription_service import TranscriptionService
from enhanced_audio_recorder import EnhancedAudioRecorder
import time

def test_transcription():
    print("=== Testing Transcription Service ===")
    
    # Create transcription service
    transcription_service = TranscriptionService()
    
    # Record a short audio clip for testing
    print("Recording 5 seconds of audio for transcription test...")
    print("Please speak clearly into your microphone...")
    
    recorder = EnhancedAudioRecorder()
    recorder.set_audio_source("microphone")
    
    try:
        filename = recorder.start_recording()
        
        # Record for 5 seconds
        for i in range(5):
            time.sleep(1)
            level = recorder.get_audio_levels()
            print(f"Recording... {i+1}/5 (Level: {level:.1f}%)")
        
        recorder.stop_recording()
        print(f"Audio recorded to: {filename}")
        
        # Test transcription
        print("\nTranscribing audio...")
        transcription = transcription_service.transcribe_audio(filename)
        
        if transcription:
            print(f"✅ Transcription successful:")
            print(f"   {transcription}")
        else:
            print("❌ No transcription returned")
            print("This could be due to:")
            print("- No internet connection for Google Speech Recognition")
            print("- Audio quality too low")
            print("- No speech detected")
            
        return bool(transcription)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_real_time_chunks():
    print("\n=== Testing Real-time Chunk Processing ===")
    
    transcription_service = TranscriptionService()
    recorder = EnhancedAudioRecorder()
    recorder.set_audio_source("microphone")
    
    print("Starting 10-second real-time transcription test...")
    print("Speak in short phrases and pause between them...")
    
    try:
        recorder.start_recording()
        
        for i in range(10):
            time.sleep(1)
            
            # Try to get and transcribe chunks
            chunk_file = recorder.get_audio_chunk()
            if chunk_file:
                transcription = transcription_service.transcribe_audio(chunk_file)
                if transcription:
                    print(f"Chunk {i+1}: {transcription}")
                else:
                    print(f"Chunk {i+1}: [No transcription]")
            else:
                print(f"Chunk {i+1}: [No audio chunk available]")
        
        recorder.stop_recording()
        print("Real-time test completed")
        
    except Exception as e:
        print(f"❌ Real-time test failed: {e}")

if __name__ == "__main__":
    print("Transcription Testing")
    print("=" * 30)
    
    # Test basic transcription
    success = test_transcription()
    
    if success:
        # Test real-time chunks if basic transcription works
        test_real_time_chunks()
    else:
        print("\nSkipping real-time test due to transcription issues")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Make sure your microphone is working")
        print("3. Speak clearly and loudly during recording")
    
    input("\nPress Enter to exit...")
