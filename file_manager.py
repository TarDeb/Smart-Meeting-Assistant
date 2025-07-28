import os
import json
from datetime import datetime

class FileManager:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "transcriptions")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_transcription(self, transcription_text, filename=None):
        """Save transcription to file"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.output_dir, f"meeting_transcription_{timestamp}.txt")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Meeting Transcription\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(transcription_text)
            
            return True
        except Exception as e:
            print(f"Error saving transcription: {e}")
            return False
    
    def save_transcription_json(self, transcription_data, filename=None):
        """Save transcription as JSON with metadata"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.output_dir, f"meeting_transcription_{timestamp}.json")
            
            data = {
                "meeting_info": {
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "time": datetime.now().strftime('%H:%M:%S'),
                    "duration": transcription_data.get('duration', 'Unknown')
                },
                "transcription": transcription_data.get('text', ''),
                "participants": transcription_data.get('participants', []),
                "summary": transcription_data.get('summary', '')
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving JSON transcription: {e}")
            return False
    
    def load_transcription(self, filename):
        """Load transcription from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading transcription: {e}")
            return None
    
    def get_transcription_files(self):
        """Get list of saved transcription files"""
        try:
            files = []
            for file in os.listdir(self.output_dir):
                if file.endswith(('.txt', '.json')):
                    filepath = os.path.join(self.output_dir, file)
                    files.append({
                        'name': file,
                        'path': filepath,
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                    })
            return sorted(files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            print(f"Error getting transcription files: {e}")
            return []
    
    def delete_transcription(self, filename):
        """Delete a transcription file"""
        try:
            os.remove(filename)
            return True
        except Exception as e:
            print(f"Error deleting transcription: {e}")
            return False
