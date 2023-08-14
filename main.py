from dataforge import config as cfg
from dataforge import database as db
import curses
import threading
import time
import os
import audioplayer
import random
import mutagen

config = cfg.Config("config.json")
songsdb = db.Database("songs", logging=False)

def centerX(string):
    return int( config.screenX / 2 ) - int( len(string) /2 )

def centerY():
    return int(config.screenY/2)

def message(text = ""):
    current.message = text
    print(text)
    
def msgpage(text = "", return_page = None):
    MessagePage.msg = text
    MessagePage.return_page = return_page
    current.page = MessagePage


class utils:
    def reload_config_from_settings():
        global config
        config = cfg.Config("config.json")
        for x in SettingsPage.options:
            if x.type in ["int", "bool"]:
                x.value = config.get(x.key)
        
    def to_minutes(seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}:{int(remaining_seconds):02d}"

    def get_duration(path):
        return mutagen.File(path).info.length
    
    def get_index(arr, index):
        if index < len(arr):
            element = arr[index]
            return element
        


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
                self.render(sc)
            except Exception as error:
                sc.addstr(0,0, f"RENDER ERROR: {error}", curses.A_REVERSE)
                print(f"RENDER ERROR: {error}")

            sc.refresh()
            
    def render(self, sc):
        sc.erase()
        
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
        if current.page == None: msgpage(f"CRASH PREVENTED: current.page set to 'None'", WelcomePage)
            
        current.page.render(sc)
        time.sleep(0.01)
        
        
            
    def deactivate(self):
        self.active = False


class keylistener_engine:
    def __init__(self):
        pass
    
    def start(self):
        curses.wrapper(self.loop)
    
    def loop(self, sc):
        current_category_index = 0
        while True:
            char = sc.getch()
            print("KEY PRESS: ",char)
            
            #process key events for current page
            try:
                current.page.process_key(char)
            except Exception as error:
                print(f"KEY PROCESSING FAILED: {error}")
                msgpage(f"KEY PROCESSING FAILED: {error}") 
            #switch category page    
            
            if char == 9: #tab
                current_category_index = (current_category_index + 1) % (len(categories)-1)
                current.page = categories[current_category_index].render_engine
                
            for category in categories:
                if char in category.shortcut_int:
                    message()
                    current.page = category.render_engine
                    current_category_index = categories.index(category)
                
                    
            
#--------
#pages

class MusicPlayerPage:
    status = item(duration=0, duration_last=time.time(), paused=False)
    player = None
    queue = []
    queue_index = 0
    
    def render(sc):
        player = MusicPlayerPage.player
        if player == None: return
        if player.path == None: metadata = {}
        else: metadata = MusicPlayerPage.player.get_metadata()
    
        status = MusicPlayerPage.status

        
        if status.duration >= metadata.get("duration", 0):
            if utils.get_index(MusicPlayerPage.queue, MusicPlayerPage.queue_index) != None:
                MusicPlayerPage.playsong(MusicPlayerPage.queue[MusicPlayerPage.queue_index].path)
                MusicPlayerPage.queue_index += 1
            else:
                MusicPlayerPage.status.paused = True
                
        if status.paused == False:
            status.duration += time.time() - status.duration_last
        status.duration_last = time.time()
        
        if player.path == None:
            sc.addstr(centerY(), centerX("No track selected"), "No track selected")
            return
        
        song = songsdb.find("path", player.path)
        line2 = f"By {song.artist}"
        sc.addstr(centerY(), centerX(song.title), song.title)
        sc.addstr(centerY()+1, centerX(line2), line2)
        
        volume = "─"*int(config.volume) + config.progressBarIcon
        sc.addstr(config.screenY-1, 0, volume)
                        
        if metadata.get("duration") != None:
            elapsed = int( (status.duration / metadata.get("duration", 0)) * 50 )
            song_progress = utils.to_minutes(status.duration) + " % " + utils.to_minutes(metadata.get("duration"))
            song_progress = song_progress.replace("%",
                    "─"*elapsed  + config.progressBarIcon + "─"*(50-elapsed) )
            sc.addstr(centerY()+3, centerX(song_progress), song_progress)
            if status.paused: sc.addstr(centerY()+4, centerX("▌▌"), "▌▌")
    
    def process_key(char):
        player = MusicPlayerPage.player
        if player == None: message('Player not loaded')
        
        match char:
            case 32: #space
                if MusicPlayerPage.status.paused:
                    MusicPlayerPage.status.paused = False
                    player.unpause()
                    message("Playing")
                else:
                    MusicPlayerPage.status.paused = True
                    player.pause()
                    message("Paused")
            
            case 259: #up
                if config.volume + 1 > 20: return
                config.volume += 1
                player.set_volume(config.volume/20)
            case 258: #down
                if config.volume - 1 < 0: return
                config.volume -= 1
                player.set_volume(config.volume/20)
            case 261: #right
                r = utils.get_index(MusicPlayerPage.queue, MusicPlayerPage.queue_index)
                if r == None: return
                MusicPlayerPage.playsong(MusicPlayerPage.queue[MusicPlayerPage.queue_index].path)
                MusicPlayerPage.queue_index += 1
            case 260: #left
                r = utils.get_index(MusicPlayerPage.queue, MusicPlayerPage.queue_index-1)
                if r == None: return
                MusicPlayerPage.queue_index -= 1
                MusicPlayerPage.playsong(MusicPlayerPage.queue[MusicPlayerPage.queue_index].path)
                
                
    def playsong(path):
        player = MusicPlayerPage.player
        if player == None: return
        
        if player.path != None: player.stop()
        player.load_audio(path)
        player.play()
        
        MusicPlayerPage.status.paused = False
        MusicPlayerPage.status.duration = 0
        MusicPlayerPage.status.duration_last = time.time()
    
    def play():
        player = audioplayer.AudioPlayer(config.volume/20)
        MusicPlayerPage.player = player
    
    def update_volume():
        player = MusicPlayerPage.player
        if player.get_volume() != config.volume/20:
            player.set_volume(config.volume/20)
        

class SettingsPage:
    options = [
        item(label="Settings", type="title"),
        item(label="Screen X", value=config.screenX, key="screenX", type="int", intmin=75, intmax=1000, description="Width of screen (Warning: Changing this may result in visual glitches)"),
        item(label="Screen Y", value=config.screenY, key="screenY", type="int", intmin=20, intmax=1000, description="Height of screen (Warning: Changing this may result in visual glitches)"),
        item(label="Exit prompt", value=config.exitPrompt, key="exitPrompt", type="bool", description="Asks for confirmation before exiting"),
        item(label="Volume", value=config.volume, key="volume", type="int", intmin=0, intmax=20, description="Change audio volume"),
        item(label="Welcome screen", value=config.welcomeScreen, key="welcomeScreen", type="bool", description="Shows a welcome screen on startup"),
        item(label="Player on select", value=config.playerOnSelect, key="playerOnSelect", type="bool", description="Opens music player when a song or playlist is selected"),
        
        item(label="Actions", type="title"),
        item(label="Save changes", type="button", action=config.save, description="Saves the settings to a file"),
        item(label="Revert changes", type="button", action=utils.reload_config_from_settings, description="Reloads config file. Beware, any unsaved changes will be lost"),
        item(label="Update volume", type="button", action=MusicPlayerPage.update_volume, description="Updates volume for the music player"),
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
            case 258: #up
                if len(SettingsPage.options) <= SettingsPage.selected+1:
                    return
                SettingsPage.selected += 1
                obj = SettingsPage.options[SettingsPage.selected]
                if obj.type == "title" and SettingsPage.selected+2 <= len(SettingsPage.options):
                    SettingsPage.selected += 1
            
            case 259: #down
                if SettingsPage.selected - 1 < 0:
                    return
                SettingsPage.selected -= 1
                obj = SettingsPage.options[SettingsPage.selected]
                if obj.type == "title" and SettingsPage.options.index(obj) != 0:
                    SettingsPage.selected -= 1
                elif obj.type == "title" and SettingsPage.options.index(obj) == 0:
                    SettingsPage.selected += 1
            
            case 260: #left
                option = SettingsPage.options[SettingsPage.selected]
                if option.type != "int": return
                if option.value - 1 < option.intmin: return
                option.value -= 1
                config.write(option.key, option.value)
            
            case 261: #right
                option = SettingsPage.options[SettingsPage.selected]
                if option.type != "int": return
                if option.value + 1 > option.intmax: return
                
                option.value += 1
                config.write(option.key, option.value)
            
            case 10: #enter
                option = SettingsPage.options[SettingsPage.selected]
                if option.type == "bool":
                    if option.value: option.value = False
                    else: option.value = True
                    
                    config.write(option.key, option.value)
                    
                elif option.type == "button":
                    option.action()
                    
                
class SongsPage:
    page = 1
    selected = 0
    results_per_page = 10
    
    def render(sc):
        results = SongsPage.get_results()
        controls1 = "[A] Previous page   [D] Next page               [Enter] Play song        "
        controls2 = "[F] Not yet         [G] Delete song             [Space] Add song to queue"
        controls3 = "[X] Add song        [C] Add song from spotify   [V] Add song from youtube"
        sc.addstr(config.screenY-3, centerX(controls1), controls1)
        sc.addstr(config.screenY-2, centerX(controls2), controls2)
        sc.addstr(config.screenY-1, centerX(controls3), controls3)
        
        if results.error: sc.addstr(centerY(), centerX("Page not found"), "Page not found")
        stats = f"Page: {SongsPage.page} - Showing {len(results.content)} out of {len(songsdb.content)} results"
        sc.addstr(3, centerX(stats), stats)
        
        sc.addstr(5,5, "TITLE", curses.A_REVERSE)
        sc.addstr(5,25, "ARTIST", curses.A_REVERSE)
        sc.addstr(5,40, "ALBUM", curses.A_REVERSE)
        sc.addstr(5,60, "DURATION", curses.A_REVERSE)
        for x in range(len(results.content)):
            if results.content.index( results.content[x] ) == SongsPage.selected: highlight = curses.A_REVERSE
            else: highlight = curses.A_BOLD
                
            r = results.content[x]
            sc.addstr(6+x,5, r.title, highlight)
            sc.addstr(6+x,25, r.artist, highlight)
            sc.addstr(6+x,40, r.album, highlight)
            if os.path.exists(r.path):
                sc.addstr(6+x,60, utils.to_minutes( utils.get_duration(r.path) ), highlight)
            else: sc.addstr(6+x,60, "MOVED/DELETED", curses.COLOR_RED)
            
        
    def get_results(page=None):
        if page == None: page = SongsPage.page
        
        results_per_page = SongsPage.results_per_page
        
        cl = songsdb.content
        pfac = results_per_page*(SongsPage.page-1)
        try: cl[pfac]
        except IndexError: return item(content=[], error=True)
        
        output = []
        for x in range(results_per_page):
            p = pfac+x
            try: c = cl[p]
            except IndexError: break
            output.append(c)
        
        return item(content=output, error=False)
    
    def process_key(char):
        results = SongsPage.get_results().content
        selected = SongsPage.selected
        if char == 258: #Down
            if SongsPage.selected + 1 >= len(results): return
            SongsPage.selected += 1
        if char == 259: #Up
            if SongsPage.selected -1 < 0: return
            SongsPage.selected -= 1
        
        if char in [97, 67, 260]: #A
            if SongsPage.page - 1 <= 0: return
            SongsPage.page -= 1
            SongsPage.selected = 0
        if char in [100, 68, 261]: #D
            if SongsPage.get_results(SongsPage.page + 1).error: return
            SongsPage.page += 1
            SongsPage.selected = 0
        if char in [102, 70]: #F
            msgpage("Not yet", SongsPage)
        if char in [103, 71]: #G
            try: song = results[selected]
            except IndexError: return
            
            songsdb.delete(song)
        if char == 32: #Space
            MusicPlayerPage.queue.append(results[selected])
        if char in [10, 459]: #Enter
            MusicPlayerPage.playsong(results[selected].path)
            if config.playerOnSelect:
                current.page = MusicPlayerPage
            

            
class PlaylistsPage:
    def render(sc):
        msg = "Playlists aren't working yet."
        sc.addstr(centerY(), centerX(msg), msg)
    
    def process_key(char): pass

    
class WelcomePage:
    def render(sc):
        msg1 = "Welcome to AudioWave"
        msg2 = "Press E to open music player"
        sc.addstr(centerY(), centerX(msg1), msg1)
        sc.addstr(centerY()+1, centerX(msg2), msg2)
    
    def process_key(char): pass
        
class KeybindsPage:
    def render(sc): pass
    
    def process_key(char): pass

class ExitPage:
    def render(sc):
        if not config.exitPrompt: os._exit(0)
        msg1 = "Are you sure you want to exit?"
        msg2 = "[Enter]  Yes"
        msg3 = "[ESC]    No "
        
        sc.addstr(centerY(), centerX(msg1), msg1)
        sc.addstr(centerY()+1, centerX(msg2), msg2)
        sc.addstr(centerY()+2, centerX(msg3), msg3)
    
    def process_key(char):
        if char == 27: #escape
            current.page = WelcomePage if config.welcomeScreen else MusicPlayerPage
        elif char in [10, 459]: #enter
            save()
            os._exit(0)
    

class MessagePage:
    msg = "No message"
    return_page = WelcomePage
    def render(sc):
        msg = MessagePage.msg
        sc.addstr(centerY(), centerX(msg), msg)
        sc.addstr(config.screenY-1, centerX("Press any key to return"), "Press any key to return")
        
    def process_key(char):
        current.page = MessagePage.return_page
#----

class current:
    page = WelcomePage if config.welcomeScreen else MusicPlayerPage
    message = ""
    playing = item(name = "")

categories = [
        category("Music Player", "E", [101, 69], MusicPlayerPage),
        category("Songs", "R", [114, 82], SongsPage),
        category("Playlists", "T", [116, 84],PlaylistsPage),
        category("Settings", "S", [115, 83], SettingsPage),
        category("Exit", "Q", [113, 81], ExitPage)
    ]

#----

def save():
    songsdb.save()
    config.save()
    MusicPlayerPage.action = item(action="exit")
    
    render.deactivate()

render = render_engine()
listener = keylistener_engine()

threading.Thread(target=render.start).start()
threading.Thread(target=listener.start).start()
threading.Thread(target=MusicPlayerPage.play).start()

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
        