import yt_dlp as ydl
import threading
from dataforge.database import Item
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import os
import random, string
from tkinter import simpledialog

class Download:
    def __init__(self, url, message_instance, db_instance):
        self.url = url
        self.message = message_instance
        self.db = db_instance

    def run_threaded(self):
        threading.Thread(target=self.run).start()

    def run(self):
        fileId = "".join(random.choice(string.ascii_letters) for _ in range(20))
        self.message("Downloading...")
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': f'songs/{fileId}.mp4',
            }

            with ydl.YoutubeDL(ydl_opts) as ydl_instance:
                ydl_instance.download([self.url])

        except Exception as e:
            self.message(f"Download error: {e}")
            return
        self.message("Processing...")
        
        file = f"songs/{fileId}.mp3"
        self.convert_to_audio(f"songs/{fileId}.mp4", file)
        
        self.message("Adding to database...")
        
        title = simpledialog.askstring("AudioWave", "Title")
        artist = simpledialog.askstring("AudioWave", "Artist")
        album = simpledialog.askstring("AudioWave", "Album")
        
        song_obj = Item(
            title=title if title != None else "Unknown Title",
            artist=artist if artist != None else "Unknown Artist",
            album=album if album != None else "Unknown Album",
            path=file)
        self.db.add(song_obj)
        
        try:
            os.remove(f"songs/{fileId}.mp4")
        except: print(f"WARNING: unable to delete 'songs/{fileId}.mp4'")
            
        self.message("Download completed")
        
        
    def convert_to_audio(self, input_path, output_path):
        video_clip = VideoFileClip(input_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_path)
    