import pygame
import time
from threading import Thread
from ..core import Config

class AudioPlayer:
    def __init__(self):
        self.volume = Config.Volume
        self.queue = {
            "index": 0,
            "queue": []
        }
        
        self.now_playing = {
            "song": None,
            "elapsed": 0, #in seconds
            "paused": True,
            
            "evl_time": 0,
        }
        
        self.running = False
        
    def set_volume(self, volume):
        self.volume = volume
        pygame.mixer_music.set_volume(volume / 100)

        Config.Volume = volume
        Config.save()
    
    def stop(self):
        self.running = False
        
    def start(self):
        self.running = True
        pygame.mixer.init()
        Thread(target=self.event_loop).start()
    
    def event_loop(self):
        while self.running:
            pygame.mixer_music.set_volume(self.volume / 100)

            if len(self.queue["queue"]) > 0:
                if not pygame.mixer_music.get_busy():
                    self.play_next()
            
            if time.time() > self.now_playing["evl_time"]:
                self.now_playing["elapsed"] += 1
                self.now_playing["evl_time"] = time.time() + 1
                
            time.sleep(0.1)
            
    def play_next(self):
        if not self.queue["index"] < len(self.queue["queue"]):
            self.queue["index"] = 0
            
        song = self.queue["queue"][self.queue["index"]]
        pygame.mixer_music.load(song.path)
        
        self.now_playing["song"] = song
        self.now_playing["elapsed"] = 0
        self.now_playing["paused"] = False
        
        self.queue["index"] += 1
        
        pygame.mixer_music.play()
        
    def play(self, song):
        if pygame.mixer_music.get_busy():
            pygame.mixer_music.stop()
        
        self.now_playing["song"] = song
        self.now_playing["elapsed"] = 0
        self.now_playing["paused"] = False
        
        pygame.mixer_music.load(song.path)
        pygame.mixer_music.play()
        
    def resume(self):
        pygame.mixer_music.unpause()
        self.now_playing["paused"] = False
        
    def pause(self):
        pygame.mixer_music.pause()
        self.now_playing["paused"] = True
        
    def seek(self, seconds):
        pygame.mixer_music.play()
        pygame.mixer_music.set_pos(seconds)
        self.now_playing["elapsed"] = seconds
        
    def skip(self, seconds):
        """use negative seconds to rewind"""
        pygame.mixer_music.play()
        pygame.mixer_music.set_pos(pygame.mixer_music.get_pos() + seconds)
        self.now_playing["elapsed"] += seconds
        
Player = AudioPlayer()
Player.start()