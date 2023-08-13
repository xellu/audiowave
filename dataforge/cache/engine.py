class item:
    def __init__(self, func, args, output):
        self.func = func
        self.args = args
        self.output = output

class memory:
    def __init__(self):
        self.memory = []
        
    def write(self, func, args, output):
        i = item(func=func, args=args, output=output)
        self.add(i)
        
    def find(self, func, args=None):
        if args != None:
            for i in self.memory:
                if i.func == func and i.args == args:
                    return i
        else:
            arr = []
            for i in self.memory:
                if i.func == func:
                    arr.append(i)
            return arr
            
    def add(self, value):
        self.memory.append(value)
    
    def delete(self, value):
        self.memory.remove(value)
        
    def clear(self):
        self.memory = []
        