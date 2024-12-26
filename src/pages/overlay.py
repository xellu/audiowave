import photon
from photon.theme import Variants
from photon.components import *

class Overlay(photon.Page):
    def __init__(self, app):
        self.app = app
        
        self.tabs = {
            #name: page
        }
        self.shortcuts = {
            #name: key
            "Home": "E"
        }
        
        for page in self.app.pages:
            self.tabs[type(page).__name__] = page
        
    def on_render(self, sc):
        self.tabs = {}
        for page in self.app.pages:
            self.tabs[type(page).__name__] = page
        
        Text(
            app = self.app,
            text = " AudioWave ".ljust(self.app.screenX, " "),
            variant = Variants.PRIMARY,
            reverse = True,
            
            x = 0,
            y = 0
        )
        
        offset = len(" AudioWave ")
        for tab in self.tabs.keys():
            Text(
                app = self.app,
                text = f" {tab} ",
                variant = Variants.PRIMARY,
                
                reverse = self.app.page != self.tabs[tab],
                
                x = offset,
                y = 0
            )
            offset += len(tab)+3
    
    def on_input(self, key):
        char = photon.keymap.get_key(key)
        if char in self.shortcuts:
            self.app.open(self.shortcuts[char])