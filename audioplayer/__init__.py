import pygame
import mutagen 

class AudioPlayer:
    def __init__(self, path, volume):
        self.path = path
        
        pygame.init()
        self.volume = volume
        self.load_audio(path)
        
    def load_audio(self, file_path):
        pygame.mixer.music.load(file_path)

    def play(self):
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def stop(self):
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
            'title': audio.get('title', 'Unknown Title'),
            'artist': audio.get('artist', 'Unknown Artist'),
            'album': audio.get('album', 'Unknown Album'),
            'duration': audio.info.length
        }
        return metadata
