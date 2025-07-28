import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import datetime
import time
import os
import glob
import webbrowser
from enhanced_audio_recorder import EnhancedAudioRecorder
from windows_audio_recorder import WindowsAudioRecorder
from transcription_service import TranscriptionService
from file_manager import FileManager

class SmartMeetingAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Meeting Assistant")
        self.root.geometry("900x700")
        
        self.enhanced_audio_recorder = EnhancedAudioRecorder()
        self.windows_audio_recorder = WindowsAudioRecorder()
        self.transcription_service = TranscriptionService()
        self.file_manager = FileManager()
        
        self.is_recording = False
        self.current_transcription = ""
        self.current_recorder = self.enhanced_audio_recorder  # Default to enhanced recorder
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Smart Meeting Assistant", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Audio source selection frame
        audio_frame = ttk.LabelFrame(main_frame, text="Audio Source", padding="5")
        audio_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.audio_source_var = tk.StringVar(value="microphone")
        
        ttk.Radiobutton(audio_frame, text="Microphone Only", 
                       variable=self.audio_source_var, value="microphone",
                       command=self.on_audio_source_change).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        ttk.Radiobutton(audio_frame, text="System Audio (YouTube, etc.)", 
                       variable=self.audio_source_var, value="system",
                       command=self.on_audio_source_change).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Radiobutton(audio_frame, text="Both (Mic + System)", 
                       variable=self.audio_source_var, value="both",
                       command=self.on_audio_source_change).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        # Test audio button
        self.test_audio_btn = ttk.Button(audio_frame, text="Test Audio Setup", 
                                        command=self.test_audio_setup)
        self.test_audio_btn.grid(row=0, column=3, sticky=tk.E)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="Start Recording", 
                                   command=self.start_recording)
        self.start_btn.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Recording", 
                                  command=self.stop_recording, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        self.save_btn = ttk.Button(control_frame, text="Save Transcription", 
                                  command=self.save_transcription)
        self.save_btn.grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        
        self.clean_btn = ttk.Button(control_frame, text="Clean Folder", 
                                   command=self.clean_folder)
        self.clean_btn.grid(row=0, column=3, padx=(0, 10), sticky=tk.W)
        
        self.github_btn = ttk.Button(control_frame, text="GitHub Repo", 
                                    command=self.open_github)
        self.github_btn.grid(row=0, column=4, sticky=tk.E)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to record", 
                                     foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=4, pady=(10, 0), sticky=tk.W)
        
        # Audio level indicator
        self.audio_level_frame = ttk.Frame(main_frame)
        self.audio_level_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(self.audio_level_frame, text="Audio Level:").grid(row=0, column=0, sticky=tk.W)
        self.audio_level_bar = ttk.Progressbar(self.audio_level_frame, length=200, mode='determinate')
        self.audio_level_bar.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)
        
        # Transcription display
        ttk.Label(main_frame, text="Meeting Transcription:", 
                 font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=4, 
                                                 pady=(20, 5), sticky=tk.W)
        
        self.transcription_text = scrolledtext.ScrolledText(main_frame, 
                                                           height=20, width=80)
        self.transcription_text.grid(row=6, column=0, columnspan=4, 
                                    pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.rowconfigure(6, weight=1)
        audio_frame.columnconfigure(3, weight=1)
        control_frame.columnconfigure(5, weight=1)
        
        # Initialize audio source
        self.on_audio_source_change()
        
    def on_audio_source_change(self):
        """Handle audio source selection change"""
        source = self.audio_source_var.get()
        
        # Always use enhanced_audio_recorder since it works properly
        self.current_recorder = self.enhanced_audio_recorder
        self.enhanced_audio_recorder.set_audio_source(source)
        
        # Update status
        source_names = {
            "microphone": "Microphone only",
            "system": "System audio (YouTube, etc.)",
            "both": "Microphone + System audio"
        }
        self.status_label.config(text=f"Ready to record - {source_names[source]}", foreground="green")
    
    def test_audio_setup(self):
        """Test and display audio setup information"""
        def show_test_results():
            try:
                # Use enhanced audio recorder for testing since it works
                test_success = self.enhanced_audio_recorder.test_system_audio_capture()
                
                # Show instructions for system audio if needed
                if self.audio_source_var.get() in ["system", "both"]:
                    stereo_mix = self.enhanced_audio_recorder.find_stereo_mix_device()
                    if not stereo_mix:
                        messagebox.showinfo("System Audio Setup", 
                            "To record system audio, please enable 'Stereo Mix' in your sound settings:\n\n"
                            "1. Right-click speaker icon\n"
                            "2. Open Sound settings\n" 
                            "3. Sound Control Panel\n"
                            "4. Recording tab\n"
                            "5. Enable 'Stereo Mix'")
                
            except Exception as e:
                messagebox.showerror("Audio Test Error", f"Error testing audio: {str(e)}")
        
        # Run test in separate thread to avoid blocking UI
        test_thread = threading.Thread(target=show_test_results)
        test_thread.daemon = True
        test_thread.start()
        
    def start_recording(self):
        self.is_recording = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        source_names = {
            "microphone": "microphone",
            "system": "system audio",
            "both": "microphone + system audio"
        }
        source = self.audio_source_var.get()
        self.status_label.config(text=f"Recording from {source_names[source]}... Speak now", foreground="red")
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self.record_and_transcribe)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # Start audio level monitoring
        self.monitor_audio_levels()
        
    def stop_recording(self):
        self.is_recording = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Processing final transcription...", foreground="orange")
        
    def record_and_transcribe(self):
        try:
            audio_file = self.current_recorder.start_recording()
            chunk_seconds = 1  # Process every 1 second for real-time
            while self.is_recording:
                chunk_file = self.current_recorder.get_audio_chunk(seconds=chunk_seconds)
                if chunk_file:
                    text = self.transcription_service.transcribe_audio(chunk_file)
                    if text:
                        self.update_transcription(text)
                time.sleep(0.2)  # Small delay to prevent excessive CPU usage
            # Final transcription (append, don't clear)
            self.current_recorder.stop_recording()
            final_text = self.transcription_service.transcribe_audio(audio_file)
            if final_text:
                self.update_transcription(final_text)
            self.root.after(0, lambda: self.finalize_transcription(None))
        except Exception as error:
            error_msg = str(error)
            self.root.after(0, lambda: self.handle_error(error_msg))
    
    def monitor_audio_levels(self):
        """Monitor and display audio levels"""
        if self.is_recording:
            try:
                level = self.current_recorder.get_audio_levels()
                self.audio_level_bar['value'] = min(level, 100)
                # Schedule next update
                self.root.after(100, self.monitor_audio_levels)
            except:
                # If there's an error getting levels, just continue
                self.root.after(100, self.monitor_audio_levels)
        else:
            self.audio_level_bar['value'] = 0
            
    def update_transcription(self, text):
        self.root.after(0, lambda: self._update_ui_transcription(text))
        
    def _update_ui_transcription(self, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {text}\n"
        self.transcription_text.insert(tk.END, formatted_text)
        self.transcription_text.see(tk.END)
        self.current_transcription += formatted_text
        
    def finalize_transcription(self, final_text):
        self.status_label.config(text="Transcription completed", foreground="green")
        # Do not clear the box, just update status
        if final_text:
            self.update_transcription(final_text)
            
    def save_transcription(self):
        if not self.current_transcription:
            messagebox.showwarning("Warning", "No transcription to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Transcription"
        )
        
        if filename:
            success = self.file_manager.save_transcription(self.current_transcription, filename)
            if success:
                messagebox.showinfo("Success", f"Transcription saved to {filename}")
            else:
                messagebox.showerror("Error", "Failed to save transcription!")
                
    def clean_folder(self):
        """Clean temporary and unnecessary files from the project folder"""
        try:
            # Get the current directory (project folder)
            project_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Define file patterns to clean
            cleanup_patterns = [
                "*.tmp",
                "*.log",
                "*.wav",
                "*.mp3",
                "temp_*",
                "chunk_*",
                "__pycache__/*",
                "*.pyc",
                "*.pyo",
                ".DS_Store",
                "Thumbs.db"
            ]
            
            # Count files before cleaning
            files_to_delete = []
            for pattern in cleanup_patterns:
                pattern_path = os.path.join(project_dir, pattern)
                files_to_delete.extend(glob.glob(pattern_path))
            
            if not files_to_delete:
                messagebox.showinfo("Clean Folder", "No temporary files found to clean.")
                return
            
            # Show confirmation dialog
            file_count = len(files_to_delete)
            confirm_msg = f"Found {file_count} temporary file(s) to delete:\n\n"
            
            # Show first few files as preview
            preview_files = files_to_delete[:5]
            for file_path in preview_files:
                confirm_msg += f"• {os.path.basename(file_path)}\n"
            
            if file_count > 5:
                confirm_msg += f"... and {file_count - 5} more files\n"
            
            confirm_msg += "\nDo you want to proceed with cleaning?"
            
            if not messagebox.askyesno("Confirm Clean", confirm_msg):
                return
            
            # Delete files
            deleted_count = 0
            failed_files = []
            
            for file_path in files_to_delete:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                    elif os.path.isdir(file_path) and "__pycache__" in file_path:
                        import shutil
                        shutil.rmtree(file_path)
                        deleted_count += 1
                except Exception as e:
                    failed_files.append(os.path.basename(file_path))
            
            # Show results
            if failed_files:
                result_msg = f"Cleaned {deleted_count} file(s).\n\nFailed to delete:\n"
                result_msg += "\n".join(failed_files)
                messagebox.showwarning("Clean Complete (with warnings)", result_msg)
            else:
                messagebox.showinfo("Clean Complete", f"Successfully cleaned {deleted_count} temporary file(s).")
            
            self.status_label.config(text=f"Folder cleaned - {deleted_count} files removed", 
                                   foreground="blue")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean folder: {str(e)}")
            self.status_label.config(text="Error during folder cleanup", foreground="red")
    
    def open_github(self):
        """Open the GitHub repository in the default web browser"""
        try:
            webbrowser.open("https://github.com/TarDeb/Smart-Meeting-Assistant")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open GitHub repository: {str(e)}")
    
    def handle_error(self, error_message):
        self.status_label.config(text=f"Error: {error_message}", foreground="red")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        messagebox.showerror("Error", f"An error occurred: {error_message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartMeetingAssistant(root)
    root.mainloop()
