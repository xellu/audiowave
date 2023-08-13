import dataforge.console as console
from dataforge.core import commands, notification

class Testing:
    def __init__(self):
        self.memory = []
    
    def test(self, func, *args, output, _print=True):
        actual_output = func(*args)
        
        if output == actual_output:
            if _print: console.info(f"{func.__name__}{args} passed the test")
            self.log()
            return True
        
        console.error(f"{func.__name__}{args} failed the test")
        return False
    
    def log(self, func, args, output):
        pass

class Input:
    def get(text:str, min_length:int=1, fallback:str="Can't accent empty input"):
        while True:
            i = input(text)
            if len(i) >= min_length:
                return i
            console.error(fallback)
            
    def multi_line(exit_command:str="exit", prefix:str=".", newline:str="> ",
                   notify:bool=True, notify_message:str="You've entered a multi-line input, use [command] to exit"):
        if notify: console.info(notify_message.replace("[command]", f"{prefix}{exit_command}"))
        content = []
        while True:
            i = input(newline)
            if i.lower() == f"{prefix}{exit_command}":
                break
            content.append(i)
        return "\n".join(content)
        

commands.register("utils", "test(func, *args, output=<output>)", "Test if the output the functions return is correct")
commands.register("utils", "Input.get(text, [min_length:int], [fallback:str])", "Gets an input string with a minimal length")
commands.register("utils", "Input.multi_line([exit_command:str], [prefix:str], [newline:str], [notify:bool], [notify_message:str])", "Allows to get input with multiple lines")

