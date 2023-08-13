import json
from dataforge.core import commands, notification
import dataforge.setup.engine as engine
import dataforge.console as console


#TODO: setup
#TODO: repair
#TODO: setup generator

class Setup():
    def __init__(self, _print: bool = True, setup_file: str = None, setup_data: dict = None):
        self._print = _print
        self.setup_file = setup_file
        self.setup_data = setup_data
        
        self.task = console.tag(console.COLOR.LIGHTCYAN_EX, "TASK").use if _print else self.void
        self.info = console.info if _print else self.void
        self.warn = console.warn if _print else self.void
        self.error = console.error if _print else self.void
        
        if setup_data == None and setup_file == None:
            raise notification.error("Please provide setup data or a setup file")
        
        for key, val in vars(self).items():
            setattr(engine.s, key, val)
        
    def void(self, *args, **kwargs): pass
        
    def start(self):
        if self.setup_data == None:
            try:
                self.setup_data = json.loads( open(self.setup_file, "r", encoding="utf-8").read() )
            except FileNotFoundError: raise notification.error("Unable to locate setup file")
        
        self.info("Setup process started")

        for x in self.setup_data:
            action = x.get("action")
            if action == None:
                self.warn("No action specified, skipping")
            else:
                engine.process_action(action, x)
    
    def repair(self):
        if self.setup_data == None:
            try:
                self.setup_data = json.loads( open(self.setup_file, "r", encoding="utf-8").read() )
            except FileNotFoundError: raise notification.error("Unable to locate setup file")
        
        engine.repair(self.setup_data)
        
def build():
    commands = ["!exit", "!save", "!load", "!actions"]
    content = []
    
    console.info("You've entered a setup building process")
    console.info("")
    console.info("Available commands:")
    for c in commands:
        console.info(c)

    console.info("")
    console.info("Available actions:")
    for a in engine.valid_actions:
        console.info(a)
    
    while True:
        i = input("> ")
        #COMMANDS
        if i.startswith("!"):
            match i.lower():
                case "!exit":
                    confirm = input("Any unsaved work will be lost. Do you wish to proceed? (Y/N): ")
                    if confirm.lower() == "y":
                        break
                    
                case "!save":
                    filename = input("File name: ")
                    open(f"{filename}.json", "w", encoding="utf-8").write( json.dumps(content, indent=4) )
                    console.info(f"Saved as {filename}.json")

                case "!load":
                    filename = input("File name: ")
                    try:
                        content = json.loads( open(f"{filename}.json", "r", encoding="utf-8").read() )
                    except Exception as err: console.error(f"Failed to load a setup: {err}")
                    else: console.info("Loaded")
                case "!actions":
                    console.info(f"Setup has {len(content)} actions")
                case _:
                    console.error("Unknown command")
        #ACTIONS      
        else:
            match i.lower():
                case "makedir":
                    path = engine.get_input("Directory Path: ", "Path cannot be empty")
                    msg = engine.get_msg()
                    content.append({"action": "MAKEDIR", "path": path, "message": msg})
                case "download":
                    path = engine.get_input("Download Path: ", "Path cannot be empty")
                    url = engine.get_input("Download URL: ", "Valid URL is required")
                    msg = engine.get_msg()
                    content.append({"action": "DOWNLOAD", "path": path, "url": url, "message": msg})
                case "makeconfig":
                    path = engine.get_input("Path: ", "Path cannot be empty")
                    console.info("Paste your json config template and use !close to close the editor")
                    while True:
                        template = engine.editor()
                        try:
                            json.loads(template)
                        except:
                            console.error("Invalid format, the template must be in JSON format")
                        else: break
                    msg = engine.get_msg()
                    content.append({"action": "MAKECONFIG", "path": path, "template": json.loads(template), "message": msg})
                case "makedb":
                    name = engine.get_input("Database Name: ", "Name cannot be empty")
                    logging = True if engine.get_input("Save database log? (Y/N): ").lower() == "y" else False
                    console.info("Paste your database content into the editor (JSON format only), use !close to close the editor")
                    while True:
                        dbcontent = engine.editor()
                        try: dbcontent = json.loads(dbcontent)
                        except: console.error("Invalid format, the content must be in JSON format")
                        else:
                            if type(dbcontent) != list:
                                dbcontent = [dbcontent]
                            break
                    content.append({"action": "MAKEDB", "name": name, "logging": logging, "content": dbcontent, "message": engine.get_msg()})
                case "makefile":
                    path = engine.get_input("File Path: ", "Path cannot be empty")
                    console.info("Paste the file content into editor, use !close to close the editor")
                    filecontent = engine.editor()
                    content.append({"action": "MAKEFILE", "path": path, "content": filecontent, "message": engine.get_msg()})
                case "script":
                    console.info("Paste the code to execute and use !close to close the editor")
                    code = engine.editor()
                    content.append({"action": "SCRIPT", "code": code, "message": engine.get_msg()})
                
#help-----
commands.register("setup", "Setup(setup_file/setup_data)", "Create a setup process")
commands.register("setup", "Setup.start()", "Start a setup process")
commands.register("setup", "Setup.repair()", "Checks for missing files, directories and repairs them")
commands.register("setup", "build()", "Allows you to make a setup process easily")
