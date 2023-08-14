import pygame
import mutagen 

class AudioPlayer:
    def __init__(self, volume):
        self.path = None
        
        pygame.init()
        self.volume = volume
        
    def load_audio(self, file_path):
        self.path = file_path
        pygame.mixer.music.load(file_path)

    def play(self):
        if self.path == None: return
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def stop(self):
        if self.path == None: return
        pygame.mixer.music.stop()

    def set_volume(self, volume):
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            pygame.mixer.music.set_volume(volume)

    def get_volume(self):
        return self.volume

    def close(self):
        pygame.mixer.quit()
        
    def get_metadata(self):
        audio = mutagen.File(self.path)
        metadata = {
            'title': audio.get('title', 'Title'),
            'artist': audio.get('artist', 'Artist'),
            'album': audio.get('album', 'Album'),
            'duration': audio.info.length
        }
        return metadata
