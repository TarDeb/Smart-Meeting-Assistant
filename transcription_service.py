import speech_recognition as sr
import os
from datetime import datetime

class TranscriptionService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio file to text"""
        if not os.path.exists(audio_file_path):
            print(f"Audio file not found: {audio_file_path}")
            return ""
            
        try:
            print(f"Attempting to transcribe: {audio_file_path}")
            with sr.AudioFile(audio_file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition first
            try:
                print("Using Google Speech Recognition...")
                text = self.recognizer.recognize_google(audio)
                print(f"Transcription successful: {text}")
                return self._format_transcription(text)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"Google Speech Recognition request failed: {e}")
                # Fallback to offline recognition
                return self._offline_transcription(audio)
                
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def _offline_transcription(self, audio):
        """Fallback offline transcription using PocketSphinx"""
        try:
            text = self.recognizer.recognize_sphinx(audio)
            return self._format_transcription(text)
        except:
            return "[Could not transcribe audio segment]"
    
    def transcribe_microphone(self, duration=5):
        """Transcribe directly from microphone"""
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source)
                print(f"Listening for {duration} seconds...")
                audio = self.recognizer.listen(source, timeout=duration)
            
            text = self.recognizer.recognize_google(audio)
            return self._format_transcription(text)
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Microphone transcription error: {e}")
            return ""
    
    def _format_transcription(self, text):
        """Format transcription with timestamp and cleanup"""
        if not text:
            return ""
            
        # Basic text cleanup
        text = text.strip()
        text = text.capitalize()
        
        # Add punctuation if missing
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {text}"
    
    def get_available_languages(self):
        """Get list of supported languages"""
        return {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
    
    def set_language(self, language_code):
        """Set the recognition language"""
        self.language = language_code
