import dataforge.core.commands as commands
import dataforge.database.engine as engine
import dataforge.database.logging as log
import dataforge.core.notification as notification
import os, json, time
import threading

Item = engine.item

#DB
class Database:
    def __init__(self, name, logging = True, debug = False):
        self.name = name + ".df.json"
        self.content = []
        self.logging = logging
        self.debug = debug
        
        if self.name not in os.listdir():
            open(self.name, "x").write("[]")
        
        self.load()
        log.info("INSTANCE CREATED", db=self)
    
    #LOADING AND SAVING DATA
    def save(self, json_indent:int = 2):
        _save = []
        for x in self.content:
            _save.append( vars(x) )
        
        open(self.name, "w", encoding="utf-8").write(
            json.dumps( _save, indent=json_indent )
        )
        log.info(f"SAVE", db=self)
    
    def load(self):
        dataset = json.loads( open( self.name, "r", encoding="utf-8" ).read() )
        for data in dataset:
            i = Item()
            for x in data:
                setattr(i, x, data[x])
            
            self.content.append( i )
        log.info(f"LOAD", db=self)
            
    def wipe(self):
        os.remove(self.name)
        log.info(f"WIPE", db=self)
    
    #SEARCHING    
    def find(self, key, query):
        for item in self.content:
            if vars(item).get(key) == query:
                log.info(f"FIND: [{key}:{query}] (FOUND)", db=self)
                return item
            
        log.info(f"FIND: [{key}:{query}] (NOT FOUND)", db=self)
        
    def findall(self, key, query):
        output = []
        for item in self.content:
            if vars(item).get(key) == query:
                output.append( item )
        
        log.info(f"FINDALL: [{key}:{query}] ({len(output)} FOUND)", db=self)
        return output
    
    #MANAGEMENT
    def delete(self, item: Item):
        self.content.remove( item )
        log.info(f"ITEM DELETE: {item.DATAFORGE_UUID}", db=self)
    
    def remove(self, item: Item):
        self.delete(item)
        log.info(f"ITEM DELETE: {item.DATAFORGE_UUID}", db=self)
        
    def add(self, item: Item):
        self.content.append( item )
        log.info(f"ITEM ADD: {item.DATAFORGE_UUID}", db=self)
        return item
    
    def create(self, item: Item):
        self.add(item)
        log.info(f"ITEM ADD: {item.DATAFORGE_UUID}", db=self)
        return item
        
    def clone(self, item: Item):
        item.DATAFORGE_UUID = engine._id()
        self.add(item)
        log.info(f"ITEM CLONE: {item.DATAFORGE_UUID}", db=self)
        return item


            
#HELP---
commands.register("database", "Database(name)", "Create a database instance")
commands.register("database", "Database.save([json indent:int])", "Saves database data to a <name>.df.json file")
commands.register("database", "Database.load", "Loads database data from a file")
commands.register("database", "Database.wipe", "Deletes database file")
commands.register("database", "Database.find(key, query)", "Finds an item in the database matching the parameters")
commands.register("database", "Database.findall(key, query)", "Finds all items in the database matching the parameters")
commands.register("database", "Database.delete(item)", "Deletes an item from the database")
commands.register("database", "Database.remove(item)", "Deletes an item from the database")
commands.register("database", "Database.add(item)", "Creates an item and adds it to the database")
commands.register("database", "Database.create(item)", "Creates an item and adds it to the database")
commands.register("database", "Database.clone(item)", "Clones the item (will have different DataForge UUID)")
