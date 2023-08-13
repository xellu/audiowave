class commands:
    def __init__(self):
        self.features = []
        
    def get(self):
        return self.features
    
    def add(self, feature):
        self.features.append(feature)
        
    def remove(self, feature):
        self.features.remove(feature)
        
class item:
    def __init__(self, category, name, description):
        self.category = category
        self.name = name
        self.description = description


cmd = commands()

def register(category, name, description):
    c = item(category, name, description)
    cmd.add(c)