from dataforge import config as cfg
from dataforge import database as db
import curses
import threading
import time
import os


config = cfg.Config("config.json")
songs = db.Database("songs", logging=False)

def centerX(string):
    return int( config.screenX / 2 ) - int( len(string) /2 )

def centerY():
    return int(config.screenY/2)

def message(text = ""):
    current.message = text

class utils:
    def reload_config_from_settings():
        global config
        config = cfg.Config("config.json")
        for x in SettingsPage.options:
            if x.type in ["int", "bool"]:
                x.value = config.get(x.key)
        

class category:
    def __init__(self, name, shortcut, shortcut_int, render_engine):
        self.name = name
        self.shortcut = shortcut
        self.shortcut_int = shortcut_int
        self.render_engine = render_engine

class item:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

#engines----------

class render_engine:
    def __init__(self):
        self.active = True
    
    def start(self):
        curses.wrapper(self.loop)
        
    def loop(self, sc):
        curses.curs_set(0)
        current.screen = sc
        while self.active:
            try:
                sc.erase()
                self.render(sc)
            except Exception as error: sc.addstr(3,3, f"RENDER ERROR: {error}")
            sc.refresh()
            
    def render(self, sc):
        
        #PAGE LIST 
        sc.addstr(0,0, " "*config.screenX, curses.A_REVERSE)
        sc.addstr(1,0, " "*config.screenX, curses.A_REVERSE)
        sc.addstr(2,0, " "*config.screenX, curses.A_REVERSE)
        sc.addstr(config.screenY,0, " "*config.screenX, curses.A_REVERSE)
        
        sc.addstr(config.screenY,1, time.strftime(config.timeformat, time.localtime()), curses.A_REVERSE)
        sc.addstr(config.screenY,config.screenX-len(current.message)-1, current.message, curses.A_REVERSE)
        
        category_offset = 1
        for i in range(len(categories)):
            category = categories[i]
            cat = f"[{category.shortcut}] {category.name}"
            
            if category.render_engine == current.page:
                sc.addstr(1, category_offset, cat)
            else:
                sc.addstr(1, category_offset, cat, curses.A_REVERSE)
            
            category_offset += len(cat)+1
            
        
        #BOTTOM BAR
        sc.addstr(1, config.screenX-len("AudioWave  "), "AudioWave", curses.A_REVERSE)
            
        #RENDER PAGE
        current.page.render(sc)
        
        
            
    def deactivate(self):
        self.active = False


class keylistener_engine:
    def __init__(self):
        pass
    
    def start(self):
        curses.wrapper(self.loop)
    
    def loop(self, sc):
        while True:
            char = sc.getch()
            print("KEY PRESS: ",char)
            
            #process key events for current page
            current.page.process_key(char)
            
            #change page
            for category in categories:
                if char in category.shortcut_int:
                    message()
                    current.page = category.render_engine
                    
            
#--------
#pages

class MusicPlayerPage:
    def render(sc):
        pass
    
    def process_key(char): pass

class SettingsPage:
    options = [
        item(label="Settings", type="title"),
        item(label="Screen X", value=config.screenX, key="screenX", type="int", intmin=75, intmax=1000, description="Width of screen (Warning: Changing this may result in visual glitches)"),
        item(label="Screen Y", value=config.screenY, key="screenY", type="int", intmin=12, intmax=1000, description="Height of screen (Warning: Changing this may result in visual glitches)"),
        item(label="Exit prompt", value=config.exitPrompt, key="exitPrompt", type="bool", description="Asks for confirmation before exiting"),
        
        item(label="Actions", type="title"),
        item(label="Save changes", type="button", action=config.save, description="Saves the settings to a file"),
        item(label="Revert changes", type="button", action=utils.reload_config_from_settings, description="Reloads config file. Beware, any unsaved changes will be lost")
    ]
    selected = 1
    
    def render(sc):
        y = 4
        message()
        for x in SettingsPage.options:
            if x.type in ["int", "bool"]:
                if SettingsPage.options.index(x) == SettingsPage.selected:
                    sc.addstr(y, 5, f"{x.label}: {x.value}", curses.A_BOLD)
                    message(x.description)
                else:
                    sc.addstr(y, 5, f"{x.label}: {x.value}")
            elif x.type == "title":
                sc.addstr(y, 5, x.label, curses.A_REVERSE)
            else:
                if SettingsPage.options.index(x) == SettingsPage.selected:
                    sc.addstr(y, 5, x.label, curses.A_BOLD)
                    message(x.description)
                else:
                    sc.addstr(y, 5, x.label)
            y += 1
            
    
    def process_key(char):
        match char:
            case 258:
                if len(SettingsPage.options) <= SettingsPage.selected+1:
                    return
                SettingsPage.selected += 1
            
            case 259:
                if SettingsPage.selected - 1 < 0:
                    return
                SettingsPage.selected -= 1
            
            case 260:
                option = SettingsPage.options[SettingsPage.selected]
                if option.type != "int": return
                if option.value - 1 < option.intmin: return
                option.value -= 1
                config.write(option.key, option.value)
            
            case 261:
                option = SettingsPage.options[SettingsPage.selected]
                if option.type != "int": return
                if option.value + 1 > option.intmax: return
                
                option.value += 1
                config.write(option.key, option.value)
            
            case 10:
                option = SettingsPage.options[SettingsPage.selected]
                if option.type == "bool":
                    if option.value: option.value = False
                    else: option.value = True
                    
                    config.write(option.key, option.value)
                    
                elif option.type == "button":
                    option.action()
        
                
            
    
class SongsPage:
    def render(sc):
        pass
    
    def process_key(char): pass
    
class PlaylistsPage:
    def render(sc):
        pass
    
    def process_key(char): pass

    
class WelcomePage:
    def render(sc):
        msg1 = "Welcome to AudioWave"
        msg2 = "Press E to open music player"
        sc.addstr(centerY(), centerX(msg1), msg1)
        sc.addstr(centerY()+1, centerX(msg2), msg2)
    
    def process_key(char): pass
        

class ExitPage:
    def render(sc):
        if not config.exitPrompt: os._exit(0)
        msg1 = "Are you sure you want to exit?"
        msg2 = "[Enter]  Yes"
        msg3 = "[Space]   No"
        
        sc.addstr(centerY(), centerX(msg1), msg1)
        sc.addstr(centerY()+1, centerX(msg2), msg2)
        sc.addstr(centerY()+2, centerX(msg3), msg3)
    
    def process_key(char):
        if char == 32:
            current.page = WelcomePage
        elif char in [10, 459]:
            save()
            os._exit(0)
    
#----

class current:
    page = WelcomePage
    message = ""
    playing = item(name = "")

categories = [
        category("Music Player", "E", [101, 69], MusicPlayerPage),
        category("Songs", "T", [116, 84], SongsPage),
        category("Playlists", "R", [114, 82], PlaylistsPage),
        category("Settings", "S", [115, 83], SettingsPage),
        category("Exit", "ESC", [27], ExitPage)
    ]

#----

def save():
    songs.save()
    config.save()
    
    render.deactivate()

render = render_engine()
listener = keylistener_engine()

threading.Thread(target=render.start).start()
threading.Thread(target=listener.start).start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        save()
        print("Exiting...")
        os._exit(0)
    except Exception as error:
        save()
        print(f"Application crashed: {error}")
        os._exit(0)
        