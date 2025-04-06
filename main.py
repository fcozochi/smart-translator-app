"""Voice Translator Pro - Final Working Version with Styling"""
import os
import tempfile
import tkinter as tk
from tkinter import ttk
from google.cloud import translate_v2 as translate
from google.cloud import speech
from google.oauth2 import service_account
from gtts import gTTS
import sounddevice as sd
import numpy as np
import wave
import pygame
from pygame import mixer

class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice Translator Pro")
        self.geometry("830x480")
        self.configure(bg="#f0f0f0")
        
        # Draggable window setup
        self.bind('<Button-1>', self.start_move)
        self.bind('<ButtonRelease-1>', self.stop_move)
        self.bind('<B1-Motion>', self.on_move)
        
        # Service initialization
        self.initialize_services()
        self.setup_audio()
        self.create_widgets()
        self.configure_styles()
        
        # Audio configuration (Original working values)
        self.current_audio_file = None
        self.recording = False
        self.frames = []
        self.sample_rate = 44100

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def stop_move(self, event):
        self._x = None
        self._y = None

    def on_move(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def initialize_services(self):
        """Original working service setup"""
        creds_file = "voice-translator-451412-8dc31221086c.json"
        try:
            if not os.path.exists(creds_file):
                raise FileNotFoundError(f"Credentials file '{creds_file}' not found")
                
            self.credentials = service_account.Credentials.from_service_account_file(
                creds_file,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            self.translate_client = translate.Client(credentials=self.credentials)
            self.speech_client = speech.SpeechClient(credentials=self.credentials)
        except Exception as e:
            print(f"Service initialization failed: {e}")
            raise

    def setup_audio(self):
        """Original audio initialization"""
        self.recording = False
        self.frames = []
        pygame.init()
        mixer.init(frequency=22050, size=-16, channels=2)

    def configure_styles(self):
        """Button styling only - your requested changes"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Record button states
        self.style.configure("Red.TButton", 
                           font=("Helvetica", 11, "bold"),
                           foreground="white",
                           background="#dc3545",
                           borderwidth=0,
                           padding=6)
        
        self.style.configure("Green.TButton", 
                           font=("Helvetica", 11, "bold"),
                           foreground="white",
                           background="#228B22",
                           borderwidth=0,
                           padding=6)
        
        # Standard buttons
        self.style.configure("Blue.TButton", 
                           font=("Helvetica", 11, "bold"),
                           foreground="white",
                           background="#2C475C",
                           borderwidth=0,
                           padding=6)
        
        # Hover effects
        self.style.map("Blue.TButton", background=[("active", "#228B22")])
        self.style.map("Red.TButton", background=[("active", "#c82333")])
        self.style.map("Green.TButton", background=[("active", "#1c6b1c")])

    def create_widgets(self):
        """UI setup with style changes only"""
        # Header
        header = tk.Label(
            self, 
            text="Smart Translator",
            font=("Helvetica", 24, "bold"),
            fg="#1a73e8",
            bg="#f0f0f0"
        )
        header.pack(pady=(10, 20))

        # Main frame
        self.main_frame = ttk.Frame(self, padding="30")
        self.main_frame.pack(expand=True, fill="both")

        # Language options
        self.languages = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh-CN",
            "Japanese": "ja",
            "Russian": "ru",
            "Arabic": "ar",
            "Igbo": "ig",
            "Yoruba": "yo",
            "Hausa": "ha"
        }

        # Language selection
        ttk.Label(self.main_frame, text="From:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.src_lang = ttk.Combobox(self.main_frame, values=list(self.languages.keys()), font=("Helvetica", 12))
        self.src_lang.set("English")
        self.src_lang.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(self.main_frame, text="To:", font=("Helvetica", 11)).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.dest_lang = ttk.Combobox(self.main_frame, values=list(self.languages.keys()), font=("Helvetica", 12))
        self.dest_lang.set("Spanish")
        self.dest_lang.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # Text areas
        text_frame = ttk.Frame(self.main_frame, borderwidth=1, relief="solid", padding="20")
        text_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        self.input_text = tk.Text(
            text_frame, 
            height=10, 
            width=40, 
            font=("Helvetica", 13),
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.input_text.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        self.output_text = tk.Text(
            text_frame, 
            height=10, 
            width=40, 
            font=("Helvetica", 13),
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.output_text.pack(side="left", expand=True, fill="both")

        # Button row
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="ew")

        # Buttons with new styling
        self.record_btn = ttk.Button(
            button_frame, 
            text="RECORD", 
            command=self.toggle_recording, 
            style="Red.TButton"
        )
        self.record_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.translate_btn = ttk.Button(
            button_frame, 
            text="TRANSLATE", 
            command=self.translate_text, 
            style="Blue.TButton"
        )
        self.translate_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.play_src_btn = ttk.Button(
            button_frame, 
            text="PLAY LANG", 
            command=self.play_source_audio,
            style="Blue.TButton"
        )
        self.play_src_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.play_trans_btn = ttk.Button(
            button_frame, 
            text="PLAY TRANS", 
            command=self.play_translated_audio,
            style="Blue.TButton"
        )
        self.play_trans_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.clear_btn = ttk.Button(
            button_frame,
            text="CLEAR",
            command=self.clear_text,
            style="Blue.TButton"
        )
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=5)

        # Grid configuration
        for i in range(4):
            self.main_frame.grid_columnconfigure(i, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

    # Original working audio methods below
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.record_btn.config(text="⏹ STOP", style="Green.TButton")
        self.frames = []
        self.audio_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback
        )
        self.audio_stream.start()

    def stop_recording(self):
        self.recording = False
        self.record_btn.config(text="RECORD", style="Red.TButton")
        self.audio_stream.stop()
        self.process_audio()

    def audio_callback(self, indata, frames, time, status):
        self.frames.append(indata.copy())

    def process_audio(self):
        audio_data = np.concatenate(self.frames, axis=0)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
            with wave.open(tmpfile.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio_data * 32767).astype(np.int16))
            self.speech_to_text(tmpfile.name)

    def speech_to_text(self, audio_file):
        try:
            with open(audio_file, 'rb') as f:
                content = f.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code=self.languages[self.src_lang.get()]
            )
            
            response = self.speech_client.recognize(config=config, audio=audio)
            if response.results:
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.END, response.results[0].alternatives[0].transcript)
        except Exception as e:
            self.output_text.insert(tk.END, f"Speech Error: {str(e)}\n")
        finally:
            try: os.unlink(audio_file)
            except: pass

    def translate_text(self):
        try:
            text = self.input_text.get(1.0, tk.END).strip()
            if text:
                result = self.translate_client.translate(
                    text,
                    target_language=self.languages[self.dest_lang.get()]
                )
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, result['translatedText'])
        except Exception as e:
            self.output_text.insert(tk.END, f"Translation Error: {str(e)}\n")

    def play_source_audio(self):
        text = self.input_text.get(1.0, tk.END).strip()
        if text:
            self.text_to_speech(text, self.languages[self.src_lang.get()])

    def play_translated_audio(self):
        text = self.output_text.get(1.0, tk.END).strip()
        if text:
            self.text_to_speech(text, self.languages[self.dest_lang.get()])

    def clear_text(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)

    def text_to_speech(self, text, lang):
        try:
            if self.current_audio_file:
                try: os.unlink(self.current_audio_file)
                except: pass
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_path)
            
            if not mixer.get_init():
                mixer.init(frequency=22050, size=-16, channels=2)
            
            mixer.music.load(temp_path)
            mixer.music.play()
            
            self.current_audio_file = temp_path
            
        except Exception as e:
            self.output_text.insert(tk.END, f"Audio Error: {str(e)}\n")
            if 'temp_path' in locals():
                try: os.unlink(temp_path)
                except: pass

if __name__ == '__main__':
    app = TranslatorApp()
    app.mainloop()