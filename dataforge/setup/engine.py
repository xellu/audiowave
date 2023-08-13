import os
import json
import time
import requests
import dataforge.config as config
import dataforge.database as database
import dataforge.console as console

class s:
    _ = None
    
def invalid(arr):
    for i in arr:
        if i == None:
            return True
    return False
    
valid_actions = ["makedir", "download", "makeconfig", "makedb", "makefile", "script"]
    
def process_action(action, data):
    try:
        action_processor(action, data)
    except Exception as e:
        s.error(f"Task failed: {e}")
    
def action_processor(action, data):
    msg = data.get("message", action)
    s.task(msg if msg != None else action)
    if action.lower() not in valid_actions:
        s.warn("Task aborted, unknown action")
        return
    
    match action.lower():
        
        case "makedir":
            path = data.get("path")
            if invalid([path]):
                s.warn("Action data missing, task skipped")
                return
            os.mkdir(path)
        
        
        case "download":
            url = data.get("url")
            path = data.get("path")
            if invalid([url, path]):
                s.warn("Action data missing, task skipped")
                return
            
            r = requests.get(url)
            if r.status_code != 200:
                s.warn("Download failed")
                return
            open(path, "wb").write(r.content)
            
        
        case "makeconfig":
            template = data.get("template")
            path = data.get("path")
            if invalid([template, path]):
                s.warn("Action data missing, task skipped")
                return
            config.create_config(path)
            open(path, "w", encoding="utf-8").write( json.dumps(template, indent=4) )
        
        
        case "makedb":
            name = data.get("name")
            if invalid([name]):
                s.warn("Action data missing, task skipped")
                return
            db = database.Database(name, logging=data.get("logging", False))
            content = data.get("content", [])
            for item in content:
                i = database.Item()
                for k, v in item.items():
                    setattr(i, k, v)
                db.add(i)
            db.save()
            
            
        case "makefile":
            path = data.get("path")
            if invalid([path]):
                s.warn("Action data missing, task skipped")
                return
            open(path, "w", encoding="utf-8").write( data.get("content", "") )
            
            
        case "script":
            code = data.get("code")
            if invalid(["code"]):
                s.warn("Action data missing, task skipped")
                return
            try:
                exec(code)
            except Exception as e:
                s.error(f"Failed to execute a script: {e}")
                
        case _:
            s.warn("Unknown action was provided, task skipped")
                
class repair:
    def __init__(self, data):
        self.data = data
        self.tasks = []
        
        start_time = time.time()
        self.scan()
        if self.tasks != []:
            s.info("Repairing files...")
            for task in self.tasks:
                process_action(task.get("action"), task)
            s.info(f"Repair completed in {time.time() - start_time:.1f}s")
        
    def scan(self):
        #directories
        for a in self.data:
            if a.get("action", "").lower() == "makedir":
                if a.get("path") != None and os.path.isdir(a.get("path")) == False:
                    self.tasks.append(a)                     
        for a in self.data:
            if a.get("action", "").lower() in ["makefile", "download", "makeconfig"]:
                #files & configs----
                if a.get("path") != None and os.path.exists(a.get("path")) == False:
                    self.tasks.append(a)
                
                #dbs----
            if a.get("action", "").lower() == "makedb":
                if a.get("name") != None and os.path.exists( f'{ a.get("name") }.df.json') == False:
                    self.tasks.append(a)
               
#BUILDER-------------     
def get_input(text:str = "", fallback: str = "Unable to accept empty input"):
    while True:
        i = input(text)
        if i != "":
            return i
        console.error(fallback)

def get_msg():
    msg = input("Custom Message (press enter to skip): ")
    if msg == "": msg = None
    return msg

def editor():
    content = []
    while True:
        i = input("| ")
        if i.lower() == "!close":
            break
        content.append(i)
    return "\n".join(content)