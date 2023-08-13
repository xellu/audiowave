import dataforge.cache.engine as engine
import dataforge.core.notification as notification
from dataforge.core import commands
import random, string

memory = engine.memory()

def use(func, _debug=False):
    def wrapper(*args):        
        search = memory.find(func, args)
        if search != None:
            if _debug:
                return str(search.output) + " [CACHE]"
            return search.output
        
        output = func(*args)
        memory.write(func, args, output)        
        
        return output
    
    return wrapper

class create:
    def __init__(self, value):
        self.value = value
        self.id = "".join(random.choice(string.ascii_lowercase) for x in range(10))
        self.args = "[MANUAL CACHE ENTRY]"
        memory.write(func = self.id, args = self.args, output = self.value)
        
    def get(self):
        s = memory.find(self.id, self.args)
        if s != None:
            return s.output
        raise notification.warn("Cache entry not found")

    def flush(self):
        flush.scope(self.id)

class flush:
    def scope(func):
        search = memory.find(func)
        for item in search:
            memory.delete(item)
            
    def all():
        memory.clear()
        
#HELP
commands.register("cache", "use", "Caching outputs for functions (use as decorator)")
commands.register("cache", "create(value)", "Create a cache entry with a custom value")
commands.register("cache", "create.get()", "Get cache entry")
commands.register("cache", "create.flush()", "Deletes cache entry")
commands.register("cache", "flush.scope(func)", "Deletes cache entries for a given function")
commands.register("cache", "flush.all()", "Deletes all cache entries")

