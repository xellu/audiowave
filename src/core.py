from dataforge import config
from dataforge.database import Database

Config = config.Config("storage/config.json")

Tracks = Database("storage/songs.json")
Playlists = Database("storage/playlists.json")