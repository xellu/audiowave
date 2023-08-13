import json
import dataforge.core.notification as notification
import dataforge.console as console
import dataforge.core.commands as commands
import dataforge.config.engine as engine

def Config(file:str = "config.json"):
    cfg = engine.Config(file=file)
    try:
        data = json.loads( open(file, "r", encoding="utf-8").read() )
    except FileNotFoundError:
        console.info(f"Creating config file")
        create_config(file)
        console.info("Config file created, proceeding")
        Config(file)
        return
    except Exception as err: raise notification.error(err)
    
    for key, val in data.items():
        setattr(cfg, key, val)
    
    return cfg

def create_config(file:str = None):
    if file == None: raise notification.error("Cannot create config file 'None'")
    try:
        open(file, "x").write("{}")
    except: raise notification.error("Config file already exists")
        
#help-----

commands.register("config", "Config(file)", "Loads/creates a config file")
commands.register("config", "create_config(file)", "Creates a config file")
commands.register("config", "Config.Set(key, value)", "Sets a key to a value")
commands.register("config", "Config.write(key, value)", "Sets a key to a value")
commands.register("config", "Config.add(key, value)", "Sets a key to a value")
commands.register("config", "Config.Get(key)", "Gets a value from a key")
commands.register("config", "Config.get(key)", "Gets a value from a key")
commands.register("config", "Config.Del(key)", "Deletes a key")
commands.register("config", "Config.delete(key)", "Deletes a key")
commands.register("config", "Config.remove(key)", "Deletes a key")
commands.register("config", "Config.save()", "Saves the config to a file")
commands.register("config", "Config.deletefile()", "Deletes the config file")

