import mutagen
from dataforge import console

class Song:
    def __init__(self,
        title: str | None = None,
        artist: str | list[str] | None = None,
        album: str | None = None,
        path: str | None = None       
    ):
        self.title = title
        self.artist = artist
        self.album = album
        self.path = path
        self.duration = 0
        
        self.load_metadata()
        
    def load_metadata(self):
        if not self.path:
            return
        
        try:
            audio = mutagen.File(self.path)
            self.duration = audio.info.length

            if not self.title:
                self.title = audio.get("title", "Unknown")
            if not self.artist:
                self.artist = audio.get("artist", "Unknown")
            if not self.album:
                self.album = audio.get("album", "Unknown")
        except Exception as e:
            console.error(f"Error loading metadata for {self.path}: {e}")
        
    def load_from_db(self, data: dict):
        for k, v in data.items():
            if k in ["title", "artist", "album", "path"]:
                setattr(self, k, v)
        self.load_metadata()
    
    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "path": self.path
        }
                
    def __str__(self):
        artist = (self.artist if isinstance(self.artist, str) else ", ".join(self.artist)) if self.artist else "Unknown"
        return f"Song('{self.title}' by {artist} - from {self.album})"
        
    def __repr__(self):
        return self.__str__()
    
    