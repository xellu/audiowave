import time

import photon
import photon.keymap
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
        
        self.windows = {
            "setVolume": {
                "open": False,
                "value": "",
                "component": Input(
                    app = self.app,
                    title = "Set Volume (0-100)",
                    variant = Variants.PRIMARY,
                    width = 25,
                    callback = self.set_volume,
                    
                    auto_render = False
                )
            },
            "warning": {
                "open": False,
                "value": "",
                "closeAt": 0,
                "component": Modal(
                    app = self.app,
                    title = "Notice (0s)",
                    variant = Variants.WARNING,
                    content = "(empty)",
                    
                    auto_render = False
                )
            }
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
            text = "  AudioWave  ".ljust(self.app.screenX, " "),
            variant = Variants.PRIMARY,
            reverse = True,
            
            x = 0,
            y = 0
        )
        
        #tabs
        offset = len("  AudioWave  ")
        for shortcut, tab in self.shortcuts.items():
            content = f"  {shortcut} | {tab}  "
            Text(
                app = self.app,
                text = content,
                variant = Variants.PRIMARY,
                
                reverse = self.app.page != self.tabs[tab],
                
                x = offset, y = 0
            )
            offset += len(content)
            
        if type(self.app.page).__name__ not in self.shortcuts.values():
            Text(
                app = self.app,
                text = f"  ❏ | {type(self.app.page).__name__}  ",
                variant = Variants.PRIMARY,
                
                x = offset, y = 0
            )
            
        #bottom
        Text(self.app, " " * self.app.screenX, 0, self.app.screenY, Variants.PRIMARY, True)
        Text(self.app, " " * self.app.screenX, 0, self.app.screenY-1, Variants.PRIMARY, True)
        Text(self.app, " " * self.app.screenX, 0, self.app.screenY-2, Variants.PRIMARY, True)
        
        #volume
        Slider( #volume slider
            app = self.app,
            value = Player.volume, max = 100,
            width = 15,
            x = self.app.screenX - 17, y = self.app.screenY - 1,
            border = False, char_pre = "█", char_post = "▒", char_point="█",
            reverse = True, variant = Variants.PRIMARY
        )
        Text( #percentage text
            app = self.app,
            text = f"{Player.volume}%".rjust(15),
            variant = Variants.PRIMARY, reverse = True,
            x = self.app.screenX - 17, y = self.app.screenY
        )
        
        #now playing
        Text(
            app = self.app,
            text = "▶" if Player.now_playing["paused"] else "■",
            y = self.app.screenY - 2,
            variant = Variants.PRIMARY, reverse = True
        )
        
        Player.now_playing["song"]        
        if not Player.now_playing["song"]:
            Text(
                app = self.app,
                text = "No song playing",
                variant = Variants.PRIMARY, reverse = True,
                x = 2, y = self.app.screenY - 1
            )
            
            Slider(
                app = self.app,
                value = 0, max = 100, width = int(self.app.screenX/3),
                char_pre = "─", char_post = "─", char_point = "⬤",
                y = self.app.screenY - 1, border = False,
                reverse = True, variant = Variants.PRIMARY
            )
        else:
            song = Player.now_playing["song"]
            Text(
                app = self.app,
                text = f"{song.title} by {song.artist}",
                variant = Variants.PRIMARY, reverse = True,
                x = 2, y = self.app.screenY - 1
            )
            
            Slider(
                app = self.app,
                value = Player.now_playing["elapsed"], max = song.duration, width = int(self.app.screenX/3),
                char_pre = "─", char_post = "─", char_point = "⬤",
                y = self.app.screenY - 1, border = False,
                reverse = True, variant = Variants.PRIMARY
            )
        
        #pop ups
        if self.windows["setVolume"]["open"]:
            self.windows["setVolume"]["component"].on_render(sc)
    
        if self.windows["warning"]["open"]:
            self.windows["warning"]["component"].title = f"Notice ({int(self.windows['warning']['closeAt'] - time.time())}s)"
            self.windows["warning"]["component"].content = self.windows["warning"]["value"]
            
            self.windows["warning"]["component"].on_render(sc)
            
            if time.time() > self.windows["warning"]["closeAt"]:
                self.windows["warning"]["open"] = False
    
    def on_input(self, key):
        if self.windows["warning"]["open"]:
            self.windows["warning"]["open"] = False
        
        char = photon.keymap.get_key(key)
        if char.upper() in self.shortcuts.keys():
            self.app.open(self.shortcuts[char.upper()])
            return photon.keymap.prevent_input()
            
        if char == "f1":
            self.app.open("Settings")
            return photon.keymap.prevent_input()
            
        if char == "q":
            Player.stop()
            self.app.exit()
            return photon.keymap.prevent_input()
            
        if key == 4: #ctrl+d
            Player.volume += 5
            if Player.volume > 100:
                Player.volume = 100
            
            Player.set_volume(Player.volume) #just in case
            return photon.keymap.prevent_input()
                
        if key == 1: #ctrl+a
            Player.volume -= 5
            if Player.volume < 0:
                Player.volume = 0
            
            Player.set_volume(Player.volume)
            return photon.keymap.prevent_input()
            
        if key == 24: #ctrl+x
            if self.windows["setVolume"]["open"]:
                self.windows["setVolume"]["value"] = ""
                
            self.windows["setVolume"]["open"] = not self.windows["setVolume"]["open"]
            return photon.keymap.prevent_input()
            
        if self.windows["setVolume"]["open"]:
            self.windows["setVolume"]["component"].on_input(key)
    
            return photon.keymap.prevent_input()

    def show_warning(self, content, timeout: int = 3):
        self.windows["warning"]["value"] = content
        self.windows["warning"]["open"] = True
        self.windows["warning"]["closeAt"] = time.time() + timeout
        
    def set_volume(self, value):
        self.windows["setVolume"]["value"] = ""
        self.windows["setVolume"]["component"].value = self.windows["setVolume"]["value"]
        
        self.windows["setVolume"]["open"] = False
        
        if not value.isdigit():
            self.show_warning("Not an integer")
            return
        
        value = int(value)
        if value < 0 or value > 100:
            self.show_warning("Out of bounds (allowed: 0-100)")
            return
        
        Player.set_volume(value)