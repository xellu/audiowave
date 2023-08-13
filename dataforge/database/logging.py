import dataforge.console as console


def _write(text, db, tag):
    open(db.name.replace(".json", ".log"), "a", encoding="utf-8").write(
        f"[{console.engine.time('%d-%m-%Y %H:%M:%S')}] [{db.name.upper()}] [{tag}] {text}\n"
    )

def info(text, db):
    if not db.logging: return
    
    if db.debug:
        console.info(text)
    _write(text, db, "INFO")

def warn(text, db):
    if not db.logging: return
    
    if db.debug:
        console.warn(text)
    _write(text, db, "WARNING")

def error(text, db):
    if not db.logging: return
    
    if db.debug:
        console.error(text)    
    _write(text, db, "ERROR")