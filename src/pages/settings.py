import photon
from photon.components import *

class Settings(photon.Page):
    def __init__(self, app):
        self.app = app
        
    def on_render(self, sc):
        pass
    
    def on_input(self, key):
        return super().on_input(key)