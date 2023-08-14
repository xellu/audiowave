import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dataforge import config

cfg = config.Config("config.json")

CLIENT_ID = ""
CLIENT_SECRET = ""

def search_and_print_track_info(track_name):
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    results = sp.search(q=track_name, type='track', limit=1)
    
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        print("Track:", track['name'])
        print("Artist:", ', '.join(artist['name'] for artist in track['artists']))
        print("Album:", track['album']['name'])
        print("Preview URL:", track['preview_url'])
    else:
        print("Track not found.")