import os
from dataforge import console

def require(files: list, error_message: str):
    listdir = os.listdir()
    for f in files:
        if f not in listdir:
            console.error(error_message.replace("%file%", f))
            input("Press enter to exit")
            os._exit(0)