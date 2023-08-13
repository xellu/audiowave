from colorama import Fore as clr

class warn(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{clr.LIGHTWHITE_EX}[DATAFORGE] {clr.YELLOW}[WARNING] {clr.LIGHTYELLOW_EX}{self.message}{clr.RESET}"
    
class warn2(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{clr.LIGHTWHITE_EX}[DATAFORGE] {clr.LIGHTRED_EX}[WARNING] {clr.LIGHTYELLOW_EX}{self.message}{clr.RESET}"
    
class error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{clr.LIGHTWHITE_EX}[DATAFORGE] {clr.RED}[ERROR] {clr.LIGHTRED_EX}{self.message}{clr.RESET}"

class info(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{clr.LIGHTWHITE_EX}[DATAFORGE] {clr.LIGHTBLUE_EX}[INFO] {clr.WHITE}{self.message}{clr.RESET}"
    
    