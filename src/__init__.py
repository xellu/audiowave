import os
from dataforge.setup import Setup
from dataforge import console

if not os.path.exists("storage"):
    Setup(setup_file="setup.json").start()
    console.info("Setup completed")
    
from .core import Config
from .utils import get_config_theme

from photon import Photon
from .pages import (
    overlay,
    
    home,
    tracks,
    playlists,
)

PAGES = [
    home.Home,
    tracks.Tracks,
    playlists.Playlists,
]

app = Photon(
    screenX = Config.ScreenX,
    screenY = Config.ScreenY,
    root = overlay.Overlay,
    theme = get_config_theme()
)

for page in PAGES:
    app.register_page(page(app))

app.open("Home")

app.run()