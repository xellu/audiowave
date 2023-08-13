class Logger:
    def __init__(self):
        self.memory = []
        self.active = False
    
    def start(self):
        self.memory = []
        self.active = True
        
    def stop(self):
        self.active = False
        
    def pause(self):
        self.active = False
    
    def resume(self):
        self.active = True
        
        
    def report(self, text):
        if self.active:
            self.memory.append(text)
            
    def save(self, path):
        open(
            path, "w", encoding="utf-8"
        ).write( "\n".join(self.memory) )
            
    def get(self, index:int = None):
        if index == None:
            return self.memory

        return self.memory[index]
        