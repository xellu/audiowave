from colorama import Fore as clr
import dataforge.console.engine as engine
import dataforge.console.logging as consolelogs
from dataforge.core import commands

COLOR = clr
logging = consolelogs.Logger()

#----------------------------

class settings:
    time = True
    time_format = "%H:%M:%S"
    uppercase = True


class util:
    def timestamp():
        if settings.time == False: return ""
        return f"{clr.LIGHTBLACK_EX}[{engine.time(settings.time_format)}] "
    
    def uppercase(string):
        if settings.uppercase: return string.upper()
        return string
    
    def process_input(string):
        for t in tags:
            string.replace(f"[{t.label}]", f"{t.color}[{t.label}]")
            string.replace(f"[{t.label.upper()}]", f"{t.color}[{t.label}]")
        return string

tags = []
class tag:
    def __init__(self, color:COLOR, label:str):
        self.color = color
        self.label = label
        tags.append(self)
        
    def print(self, text):
        text = f"{util.timestamp()}{self.color}[{util.uppercase(self.label)}] {clr.RESET}{text}"
        logging.report(text)
        print(text)
        
    def delete(self):
        tags.remove(self)

def modify(setting, value):
    setattr(settings, setting, value)

#------------------------------

info = tag(clr.LIGHTBLUE_EX, "Info").print
warn = tag(clr.YELLOW, "Warning").print
error = tag(clr.RED, "Error").print

def log(text):
    text = util.process_input(text)
    text = f"{util.timestamp()}{clr.RESET}{text}{clr.RESET}"
    logging.report(text)
    print(text)

#HELP---
commands.register("console", "tag(<color>, <label>)", "Creates a console tag")
commands.register("console", "tag.print(<text>)", "Prints a message using console tag")
commands.register("console", "modify(<setting>, <value>)", "Changes display settings for console tags")
commands.register("console", "log(<text>)", "Prints text to console")
commands.register("console", "info(<text>)", "Prints informational message (default console tag)")
commands.register("console", "warn(<text>)", "Prints warning message (default console tag)")
commands.register("console", "error(<text>)", "Prints error message (default console tag)")
