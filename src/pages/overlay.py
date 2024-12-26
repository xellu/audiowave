import photon
from photon.theme import Variants
from photon.components import *

from ..player import Player

class Overlay(photon.Page):
    def __init__(self, app):
        self.app = app
        
        self.tabs = {
            #name: page
        }
        self.shortcuts = {
            #name: key
            "E": "Home",
            "R": "Playlists",
            "T": "Tracks",
        }
        
        for page in self.app.pages:
            self.tabs[type(page).__name__] = page
        
    def on_render(self, sc):
        self.tabs = {}
        for page in self.app.pages:
            self.tabs[type(page).__name__] = page
        
        #branding
        Text(
            app = self.app,
            text = " AudioWave ".ljust(self.app.screenX, " "),
            variant = Variants.PRIMARY,
            reverse = True,
            
            x = 0,
            y = 0
        )
        
        #tabs
        offset = len(" AudioWave ")
        for shortcut, tab in self.shortcuts.items():
            content = f" ({shortcut}) {tab} "
            Text(
                app = self.app,
                text = content,
                variant = Variants.PRIMARY,
                
                reverse = self.app.page != self.tabs[tab],
                
                x = offset,
                y = 0
            )
            offset += len(content)
            
        #bottom
        Text(self.app, " " * self.app.screenX, 0, self.app.screenY, Variants.PRIMARY, True)
        Text(self.app, " " * self.app.screenX, 0, self.app.screenY-1, Variants.PRIMARY, True)
        Text(self.app, " " * self.app.screenX, 0, self.app.screenY-2, Variants.PRIMARY, True)
        
        #volume
        Slider( #volume slider
            app = self.app,
            value = Player.volume, max = 100,
            width = 15,
            x = self.app.screenX - 16, y = self.app.screenY - 1,
            border = False, char_pre = "─", char_post = " ", char_point="⎔",
            reverse = True, variant = Variants.PRIMARY
        )
        Text( #percentage text
            app = self.app,
            text = f"{Player.volume}%".rjust(10),
            variant = Variants.PRIMARY, reverse = True,
            x = self.app.screenX - 16, y = self.app.screenY
        )
    
    def on_input(self, key):
        char = photon.keymap.get_key(key)
        if char.upper() in self.shortcuts.keys():
            self.app.open(self.shortcuts[char.upper()])
            
        if char == "q":
            Player.stop()
            self.app.exit()
            
        return photon.keymap.prevent_input()