import dataforge.core.commands as commands
import dataforge.cache as cache
import dataforge.console as console
import dataforge.database as database

__version__ = '1.0.0'

def help(_print:bool = True):
    out = []
    for c in commands.cmd.get():
        out.append(f"{c.category}.{c.name}  -  {c.description} ")
    
    out = "\n".join(out)
    if _print:
        print(out)
    return out