import json
import os

class Config:
    def __init__(self, file, **kwargs):
        self.DATAFORGE_FILE = file
        for var, val in kwargs.items():
            setattr(self, var, val)

    def Set(self, key, value):
        setattr(self, key, value)
    write = Set
    add = Set
    
    def Get(self, key):
        return getattr(self, key)
    get = Get
    
    def Del(self, key):
        delattr(self, key)
    delete = Del
    remove = Del
    
    def save(self):
        file = self.DATAFORGE_FILE
        delattr(self, "DATAFORGE_FILE")
        
        open(file, "w", encoding="utf-8").write( json.dumps( vars(self), indent=4 ) )
        
        setattr(self, "DATAFORGE_FILE", file)
        
    def deletefile(self):
        os.remove(self.DATAFORGE_FILE)