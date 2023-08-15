import pypresence
import time
from dataforge.database import Item

class Presence:
    def __init__(self, app_id):
        self.app_id = app_id
        self.rpc = pypresence.Presence(app_id)
        self.state = Item(title="Idle", description="https://github.com/xellu/audiowave")

    def connect(self):
        self.rpc.connect()

    def update(self):
        self.rpc.update(
            state=self.state.description,
            details=self.state.title,
            large_image='audiowaveresize',
            large_text='AudioWave',
            buttons=[{"label": "Get AudioWave", "url": "https://github.com/xellu/audiowave"}],
        )

    def set_state(self, state):
        self.state = state
            