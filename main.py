print("[AudioWave] Application is booting up...")

#TODO: download playlist from youtube

from dataforge import config as cfg
from dataforge import database as db
from dataforge import cache
import curses
import threading
import time
import os
import random
import string
import mutagen
from tkinter import simpledialog
from engine import youtube, discordrpc, startup_requirements, audioplayer

startup_requirements.require(
        files = ["playlists.df.json", "songs.df.json", "config.json", "songs"],
        error_message = "[!] Application unable, because %file% is missing. re-run setup and try again. If the issue persists report this issue here: https://github.com/xellu/audiowave/issues"
    )

version = "1.1.0"
config = cfg.Config("config.json")
songsdb = db.Database("songs", logging=False)
playlistsdb = db.Database("playlists", logging=False)
RPCCon = False

def centerX(string):
    return int( config.screenX / 2 ) - int( len(string) /2 )

def centerXint(num):
    return int( config.screenX / 2 ) - int( num/2 )


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
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60

        if hours > 0:
            return f"{int(hours)}:{int(minutes):02d}:{int(remaining_seconds):02d}"
        return f"{int(minutes)}:{int(remaining_seconds):02d}"


    @cache.use
    def get_duration(path):
        return mutagen.File(path).info.length
    
    def get_index(arr, index):
        if index < len(arr):
            element = arr[index]
            return element
        
    def open_keybind_page():
        current.page = KeybindsPage
    
    def open_info_page():
        current.page = InfoPage
        
    def set_rpc(state):
        if not RPCCon: print("RPC is not connected")
        
        rpc.set_state(state)
        
    def get_playlist_duration(songs: list):
        dur = 0
        for song in songs:
            dur += utils.get_duration(song)
        return dur
        
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
        
        sc.addstr(config.screenY,config.screenX-len(current.message)-1, current.message, curses.A_REVERSE)
        
        #VOLUME BAR
        volume = f"{str(int( (config.volume/20)*100 ))}% "
        if config.volume == 0: volume += "🔇"
        else: volume += "─"*int(config.volume/2) + config.progressBarIcon
        sc.addstr(config.screenY, 0, volume, curses.A_REVERSE)
        
        #CATEGORY BAR
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
        if current.page == None: msgpage(f"CRASH PREVENTED: current.page set from {None} to {WelcomePage}", WelcomePage)
            
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
                msgpage(f"KEY PROCESSING FAILED: {error}", current.page) 
            #switch category page    
            
            if char == 9: #tab
                message()
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

        if player.path == None:
            sc.addstr(centerY(), centerX("No track selected"), "No track selected")
            return
        
        song = songsdb.find("path", player.path)
        line2 = f"By {song.artist}"
        sc.addstr(centerY(), centerX(song.title), song.title)
        sc.addstr(centerY()+1, centerX(line2), line2)
        
                        
        if metadata.get("duration") != None:
            elapsed = int( (status.duration / metadata.get("duration", 0)) * 50 )
            bar = utils.to_minutes(status.duration) + " % " + utils.to_minutes(metadata.get("duration"))
            song_progress = bar.replace("%",
                    "─"*elapsed  + config.progressBarIcon + "─"*(50-elapsed) )
            sc.addstr(centerY()+3, centerX(song_progress), song_progress)
            if status.paused: sc.addstr(centerY()+4, centerX("▌▌"), "▌▌")
            
    def loop_thread():
        while True:
            try:
                MusicPlayerPage.loop()
                time.sleep(0.1)
            except Exception as e:
                print(f"Player Error: {e}")
    
    def loop():
        player = MusicPlayerPage.player
        if player == None: return
        if player.path == None: metadata = {}
        else: metadata = MusicPlayerPage.player.get_metadata()
    
        status = MusicPlayerPage.status
        
        if (MusicPlayerPage.queue_index + 1 > len(MusicPlayerPage.queue) - 1) and config.musicLoop:
            MusicPlayerPage.queue_index = 0
        
        if status.duration >= metadata.get("duration", 0):
            if utils.get_index(MusicPlayerPage.queue, MusicPlayerPage.queue_index+1) != None:
                MusicPlayerPage.queue_index += 1
                MusicPlayerPage.playsong(MusicPlayerPage.queue[MusicPlayerPage.queue_index].path)
            else:
                utils.set_rpc(item(title="Idle", description="https://github.com/xellu/audiowave"))
                MusicPlayerPage.status.paused = True
                
        if status.paused == False:
            status.duration += time.time() - status.duration_last
        status.duration_last = time.time()
        
        song = songsdb.find("path", player.path)
        if RPCCon and player.path != None:
            bar = utils.to_minutes(status.duration) + " % " + utils.to_minutes(metadata.get("duration"))
            mini_elapsed = int( (status.duration / metadata.get("duration", 0)) * 10 )
            mini_song_progress = bar.replace("%", "─"*mini_elapsed  + config.progressBarIcon + "─"*(10-mini_elapsed) )
            if status.paused: mini_song_progress += " ⏸️"
            utils.set_rpc( item(title=f"Listening to {song.title} by {song.artist}", description=mini_song_progress) )
    
    def process_key(char):
        player = MusicPlayerPage.player
        if player == None: message('Player not loaded')
        
        
        if char == 32: #space
                if MusicPlayerPage.status.paused:
                    MusicPlayerPage.status.paused = False
                    player.unpause()
                    message("Playing")
                else:
                    MusicPlayerPage.status.paused = True
                    player.pause()
                    message("Paused")
            
        if char == 259: #up
            if config.volume + 1 > 20: return
            config.volume += 1
            player.set_volume(config.volume/20)
        if char == 258: #down
            if config.volume - 1 < 0: return
            config.volume -= 1
            player.set_volume(config.volume/20)
        if char == 261: #right
            r = utils.get_index(MusicPlayerPage.queue, MusicPlayerPage.queue_index)
            if r == None: return
            MusicPlayerPage.queue_index += 1
            MusicPlayerPage.playsong(MusicPlayerPage.queue[MusicPlayerPage.queue_index].path)
        if char == 260: #left
            if MusicPlayerPage.queue_index == 0: return
            MusicPlayerPage.queue_index -= 1
            MusicPlayerPage.playsong(MusicPlayerPage.queue[MusicPlayerPage.queue_index].path)
        if char in [97, 67]: #A
            if MusicPlayerPage.status.duration - config.skipRadius < 0:
                MusicPlayerPage.status.duration = 0
            else: MusicPlayerPage.status.duration -= config.skipRadius
            player.seek(MusicPlayerPage.status.duration)
            if MusicPlayerPage.status.paused: player.pause()
        if char in [100, 68]: #D
            max_duration = player.get_metadata().get("duration", 0)
            if MusicPlayerPage.status.duration + config.skipRadius > max_duration:
                MusicPlayerPage.status.duration = max_duration
            else: MusicPlayerPage.status.duration += config.skipRadius
            player.seek(MusicPlayerPage.status.duration)
            if MusicPlayerPage.status.paused: player.pause()
        
                
                
    def playsong(path):
        player = MusicPlayerPage.player
        if player == None: return
        
        if player.path != None: player.stop()
        player.load_audio(path)
        player.play(fadeIn = config.audioFade)
        
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
        item(label="Loop queue", value=config.musicLoop, key="musicLoop", type="bool", description="Loops songs in a queue"),
        item(label="Shuffle queue", value=config.musicShuffle, key="musicShuffle", type="bool", description="Plays songs from queue in random order"),
        item(label="Audio Fade", value=config.audioFade, key="audioFade", type="bool", description="Increases the volume with time (track fades in)"),
        item(label="Skip Radius", value=config.skipRadius, key="skipRadius", type="int", intmin=1, intmax=60, description="The amount of seconds to go forward/backward when skipping"),

        item(label="Actions", type="title"),
        item(label="Save changes", type="button", action=config.save, description="Saves the settings to a file"),
        item(label="Revert changes", type="button", action=utils.reload_config_from_settings, description="Reloads config file. Beware, any unsaved changes will be lost"),
        item(label="Update volume", type="button", action=MusicPlayerPage.update_volume, description="Updates volume for the music player"),
        item(label="Keybinds", type="button", action=utils.open_keybind_page, description="List of all keybinds"),
        item(label="About", type="button", action=utils.open_info_page, description="Information about AudioWave application")
    ]
    selected = 1
    
    def render(sc):
        y = 4
        message()
        for x in SettingsPage.get_results():
            if x.type in ["int", "bool"]:
                if SettingsPage.options.index(x) == SettingsPage.selected:
                    sc.addstr(y, 5, f"{x.label}: {x.value}", curses.A_REVERSE)
                    message(x.description)
                else:
                    sc.addstr(y, 5, f"{x.label}: {x.value}")
            elif x.type == "title":
                sc.addstr(y, 5, x.label, curses.A_REVERSE)
            else:
                if SettingsPage.options.index(x) == SettingsPage.selected:
                    sc.addstr(y, 5, x.label, curses.A_REVERSE)
                    message(x.description)
                else:
                    sc.addstr(y, 5, x.label)
            y += 1

    def get_results():
        if config.screenY - 5 - len(SettingsPage.options) < 0:
            output = []
            for i in range(config.screenY-5):
                x = i+SettingsPage.selected
                try:
                    output.append(SettingsPage.options[x])
                except IndexError: break
            return output
        else: return SettingsPage.options
            
    
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
    db = songsdb
    error404 = "You have no songs added, use [X] or [C] to add them"
    search404 = "No results found"
    
    select = item(mode = False, output = [], return_page = None, callback = None)
    
    def render(sc):
        SongsPage.results_per_page = config.screenY - 10
        results = SongsPage.get_results()
        if len(results.content) == 0 and not len(SongsPage.db.content) == 0: SongsPage.page -= 1
        
        controls1 = "[A] Previous page    [D] Next page                    [Enter] Play song    "
        controls2 = "[B] Edit details     [G] Delete song                  [Space] Add to queue "
        controls3 = "[X] Add song         [C] Add song from youtube        [F] Search           "                         
        if SongsPage.select.mode:                                                                   #
            controls1 = "[A] Previous page    [D] Next page                    [Enter] Select       "
            controls2 = "[B] Edit details     [G] Delete song                  [ESC] Save & Exit    "
        
        
        sc.addstr(config.screenY-3, centerX(controls1), controls1)
        sc.addstr(config.screenY-2, centerX(controls2), controls2)
        sc.addstr(config.screenY-1, centerX(controls3), controls3)
        
        if results.error:
            if SongsPage.db == songsdb: sc.addstr(centerY(), centerX(SongsPage.error404), SongsPage.error404)
            else: sc.addstr(centerY(), centerX(SongsPage.search404), SongsPage.search404)
        
        stats = f"Page: {SongsPage.page} - Showing {len(results.content)} out of {len(SongsPage.db.content)} results"
        sc.addstr(3, centerX(stats), stats)
        
        sc.addstr(5, centerXint(25)-30, "TITLE", curses.A_REVERSE)
        sc.addstr(5, centerXint(15)-5, "ARTIST", curses.A_REVERSE)
        sc.addstr(5, centerXint(20)+15, "ALBUM", curses.A_REVERSE)
        sc.addstr(5, centerXint(8)+30, "DURATION", curses.A_REVERSE)
        for x in range(len(results.content)):
            if results.content.index( results.content[x] ) == SongsPage.selected or (
                SongsPage.select.mode and results.content[x] in SongsPage.select.output): highlight = curses.A_REVERSE
            else: highlight = curses.A_BOLD
                
            r = results.content[x]
            sc.addstr(6+x, centerXint(25)-30, r.title[:24], highlight)
            sc.addstr(6+x, centerXint(15)-5, r.artist[:14], highlight)
            sc.addstr(6+x, centerXint(20)+15, r.album[:19], highlight)
            if os.path.exists(r.path):
                sc.addstr(6+x,centerXint(8)+30, utils.to_minutes( utils.get_duration(r.path) ), highlight)
            else: sc.addstr(6+x,centerXint(8)+30, "MOVED/DELETED", curses.COLOR_RED)
            
        
    def get_results(page=None):
        if page == None: page = SongsPage.page
        results_per_page = SongsPage.results_per_page
        
        cl = SongsPage.db.content
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
            if SongsPage.selected + 1 >= len(results):
                SongsPage.selected = 0
                return
            SongsPage.selected += 1
        if char == 259: #Up
            if SongsPage.selected -1 < 0:
                SongsPage.selected = len(SongsPage.get_results().content)-1 
                return
            SongsPage.selected -= 1
        
        if char in [97, 67, 260]: #A/Left
            if SongsPage.page - 1 <= 0: return
            SongsPage.page -= 1
            SongsPage.selected = 0
        if char in [100, 68, 261]: #D/Right
            if SongsPage.get_results(SongsPage.page + 1).error: return
            SongsPage.page += 1
            SongsPage.selected = 0
        if char in [98, 66]: #B
            SongEditPage.open(results[selected])
            
        if char in [103, 71, 330]: #G/Del
            try: song = results[selected]
            except IndexError: return
            
            SongsPage.selected = 0
            songsdb.delete(song)
        
        if char == 32 and SongsPage.select.mode == False: #Space
            MusicPlayerPage.queue.append(results[selected])
        if char in [10, 459] and SongsPage.select.mode == False: #Enter
            MusicPlayerPage.playsong(results[selected].path)
            if config.playerOnSelect:
                current.page = MusicPlayerPage
            
        if char in [120, 88]: #X
            path = simpledialog.askstring("AudioWave", "Path to mp3 file")
            if path == None:
                message("Cancelled")
                return
            if os.path.isfile(path) == False:
                message("Audio file not found")
                return
            if path.endswith(".mp3") == False:
                message("Unsupported file format")
                return

            title = simpledialog.askstring("AudioWave", "Title")
            artist = simpledialog.askstring("AudioWave", "Artist")
            album = simpledialog.askstring("AudioWave", "Album")
            
            song = db.Item(title=str(title), artist=str(artist), album=str(album), path=path)
            songsdb.add(song)
            message("Song added")
        
        if char in [99, 67]: #C
            url = simpledialog.askstring("AudioWave", "Youtube URL")
            if url == None:
                message("Cancelled")
                return
            youtube.Download(url, message_instance=message, db_instance=songsdb).run_threaded()
            
        if char in [102, 70]: #F
            if SongsPage.db != songsdb:
                SongsPage.db = songsdb
                return
            
            query = simpledialog.askstring("Search", "Prompt")
            if query == None: return

            searchdb = item(content=[])
            SongsPage.db = searchdb
            
            for song in songsdb.content:
                if ( query.lower() in song.title.lower() or
                query.lower() in song.artist.lower() or
                query.lower() in song.album.lower() or 
                query.lower() in song.path.lower() ):
                    searchdb.content.append(song)
                    
        #---SELECT MODE---
        if char in [10, 429] and SongsPage.select.mode: #enter
            song = results[selected]
            if song in SongsPage.select.output:
                SongsPage.select.output.remove(song)
            else:
                SongsPage.select.output.append(song)       
        if char in [27]: #esc
            SongsPage.select.mode = False
            SongsPage.select.callback(SongsPage.select.output)
            current.page = SongsPage.select.return_page
            
class PlaylistPage:
    playlist = None
    def open(playlist):
        PlaylistPage.playlist = playlist
        current.page = PlaylistPage
        
    page = 1
    selected = 0
    results_per_page = 10

    
    def render(sc):
        if PlaylistPage.playlist == None:
            sc.addstr(centerY(), centerX("No playlist selected"), "No playlist selected")
            return
        
        PlaylistPage.results_per_page = config.screenY - 11
        results = PlaylistPage.get_results()
        if len(results.content) == 0 and not len(PlaylistPage.playlist.songs) == 0: PlaylistPage.page -= 1
        
        controls1 = "[A] Previous page          [D] Next page         [B] Edit details          "
        controls2 = "[G] Remove from playlist   [X] Add to playlist   [Enter] Play song         "
        sc.addstr(config.screenY-2, centerX(controls1), controls1)
        sc.addstr(config.screenY-1, centerX(controls2), controls2)
        
    
        if results.error:
            sc.addstr(centerY(), centerX("Playlist is empty"), "Playlist is empty")
        
        stats = f"Page: {PlaylistPage.page} - Showing {len(results.content)} out of {len(PlaylistPage.playlist.songs)} results"
        sc.addstr(3, centerX(stats), stats)
        sc.addstr(5, centerX(PlaylistPage.playlist.name), PlaylistPage.playlist.name, curses.A_REVERSE)
        
        sc.addstr(7, centerXint(25)-30, "TITLE", curses.A_REVERSE)
        sc.addstr(7, centerXint(15)-5, "ARTIST", curses.A_REVERSE)
        sc.addstr(7, centerXint(20)+15, "ALBUM", curses.A_REVERSE)
        sc.addstr(7, centerXint(8)+30, "DURATION", curses.A_REVERSE)
        for x in range(len(results.content)):
            if results.content.index( results.content[x] ) == PlaylistPage.selected: highlight = curses.A_REVERSE
            else: highlight = curses.A_BOLD
                
            r = songsdb.find("path", results.content[x])
            if r == None: r = item(title="(DELETED)", artist="Artist", album="Album", path="")
             
            sc.addstr(8+x, centerXint(25)-30, r.title[:24], highlight)
            sc.addstr(8+x, centerXint(15)-5, r.artist[:14], highlight)
            sc.addstr(8+x, centerXint(20)+15, r.album[:19], highlight)
            if os.path.exists(r.path):
                sc.addstr(8+x,centerXint(8)+30, utils.to_minutes( utils.get_duration(r.path) ), highlight)
            else: sc.addstr(8+x,centerXint(8)+30, "MOVED/DELETED", curses.COLOR_RED)
            
        
    def get_results(page=None):
        if page == None: page = PlaylistPage.page
        results_per_page = PlaylistPage.results_per_page
        
        cl = PlaylistPage.playlist.songs
        pfac = results_per_page*(PlaylistPage.page-1)
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
        if PlaylistPage.playlist == None: return
        results = PlaylistPage.get_results().content
        selected = PlaylistPage.selected
        if char == 258: #Down
            if PlaylistPage.selected + 1 >= len(results):
                PlaylistPage.selected = 0
                return
            PlaylistPage.selected += 1
        if char == 259: #Up
            if PlaylistPage.selected -1 < 0:
                PlaylistPage.selected = len(PlaylistPage.get_results().content)-1 
                return
            PlaylistPage.selected -= 1
        
        if char in [97, 67, 260]: #A/Left
            if PlaylistPage.page - 1 <= 0: return
            PlaylistPage.page -= 1
            PlaylistPage.selected = 0
        if char in [100, 68, 261]: #D/Right
            if PlaylistPage.get_results(PlaylistPage.page + 1).error: return
            PlaylistPage.page += 1
            PlaylistPage.selected = 0
        if char in [98, 66]: #B
            SongEditPage.open(
                songsdb.find("path", results[selected])
            )
        if char in [103, 71, 330]: #G/DEL
            song = results[selected]
            if song in PlaylistPage.playlist.songs:
                PlaylistPage.playlist.songs.remove(song)
            PlaylistPage.selected = 0
        if char in [120, 88]: #X            
            songs = []
            for s in PlaylistPage.playlist.songs:
                song = songsdb.find("path", s)
                if song != None: songs.append(song)
            SongsPage.select = item(mode=True, output = songs, return_page = PlaylistPage, callback = PlaylistPage.edit_playlist_callback)
            current.page = SongsPage
        if char in [10, 459]: #Enter
            MusicPlayerPage.playsong(results[selected])
    
    def edit_playlist_callback(songs):
        if len(songs) == 0:
            playlistsdb.delete(PlaylistPage.playlist)
            return
        
        song_paths = []
        for s in songs:
            song_paths.append(s.path)
        
        PlaylistPage.playlist.songs = song_paths
        
class PlaylistEditPage:
    playlist = item(name="Unknown Playlist")
    options = [
        item(value=playlist.name, attr="name")
    ]
    selected = 0
    
    def open(playlist):
        PlaylistEditPage.playlist = playlist
        PlaylistEditPage.options = [
            item(value=playlist.name, attr="name"),
        ]
        current.page = PlaylistEditPage
    
    def render(sc):    
        controls = "[Enter] Edit   [ESC] Return"
        sc.addstr(config.screenY-1, centerX(controls), controls)
        
        sc.addstr(4,5, "NAME   ", curses.A_REVERSE)
        for x in range(len(PlaylistEditPage.options)):
            if PlaylistEditPage.selected == x: sc.addstr(4+x, 13, str(PlaylistEditPage.options[x].value), curses.A_REVERSE)
            else: sc.addstr(4+x, 13, str(PlaylistEditPage.options[x].value))
        
        
        
    def process_key(char):
        if PlaylistEditPage.playlist == None:
            current.page = PlaylistListPage
            return
        
        if char == 259: #down
            if PlaylistEditPage.selected - 1 < 0: return
            PlaylistEditPage.selected -= 1 
        if char == 258: #up
            if PlaylistEditPage.selected + 1 > len(PlaylistEditPage.options)-1: return
            PlaylistEditPage.selected += 1
        if char in [10, 459]: #enter
            selected = PlaylistEditPage.options[PlaylistEditPage.selected]
            new_val = simpledialog.askstring("AudioWave", selected.attr)
            if new_val == None:
                message("Cancelled")
                return
            playlist = playlistsdb.find("songs", PlaylistEditPage.playlist.songs)
            setattr(playlist, selected.attr, new_val)
            PlaylistEditPage.open(playlist)
        if char in [27]: #escape
            current.page = PlaylistListPage        
class PlaylistListPage:
    page = 1
    selected = 0
    results_per_page = 10
    db = playlistsdb
    error404 = "You have no playlists, press [X] or [C] to create one"
    search404 = "No results found"
    
    def render(sc):
        PlaylistListPage.results_per_page = config.screenY - 10
        results = PlaylistListPage.get_results()
        if len(results.content) == 0 and not len(PlaylistListPage.db.content) == 0: PlaylistListPage.page -= 1
        
        controls1 = "[A] Previous page    [D] Next page                    [Enter] Play playlist"
        controls2 = "[B] Edit details     [G] Delete playlist              [Space] Open playlist"
        controls3 = "[X] Create playlist  [C] Add playlist from youtube    [F] Search           "
        sc.addstr(config.screenY-3, centerX(controls1), controls1)
        sc.addstr(config.screenY-2, centerX(controls2), controls2)
        sc.addstr(config.screenY-1, centerX(controls3), controls3)
    
        if results.error:
            if PlaylistListPage.db == playlistsdb: sc.addstr(centerY(), centerX(PlaylistListPage.error404), PlaylistListPage.error404)
            else: sc.addstr(centerY(), centerX(PlaylistListPage.search404), PlaylistListPage.search404)    
        
        stats = f"Page: {PlaylistListPage.page} - Showing {len(results.content)} out of {len(PlaylistListPage.db.content)} results"
        sc.addstr(3, centerX(stats), stats)
        
        sc.addstr(5, centerXint(25)-15, "NAME", curses.A_REVERSE)
        sc.addstr(5, centerXint(15)+10, "SONGS", curses.A_REVERSE)
        sc.addstr(5, centerXint(8)+15, "DURATION", curses.A_REVERSE)
        for x in range(len(results.content)):
            if results.content.index( results.content[x] ) == PlaylistListPage.selected: highlight = curses.A_REVERSE
            else: highlight = curses.A_BOLD
                
            r = results.content[x]
            sc.addstr(6+x, centerXint(25)-15, r.name[:24], highlight)
            sc.addstr(6+x, centerXint(15)+10, str( len(r.songs) ), highlight)
            sc.addstr(6+x,centerXint(8)+15, utils.to_minutes( utils.get_playlist_duration(r.songs) ), highlight)
            
        
    def get_results(page=None):
        if page == None: page = PlaylistListPage.page
        results_per_page = PlaylistListPage.results_per_page
        
        cl = PlaylistListPage.db.content
        pfac = results_per_page*(PlaylistListPage.page-1)
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
        results = PlaylistListPage.get_results().content
        selected = PlaylistListPage.selected
        if char == 258: #Down
            if PlaylistListPage.selected + 1 >= len(results):
                PlaylistListPage.selected = 0
                return
            PlaylistListPage.selected += 1
        if char == 259: #Up
            if PlaylistListPage.selected -1 < 0:
                PlaylistListPage.selected = len(PlaylistListPage.get_results().content)-1 
                return
            PlaylistListPage.selected -= 1
        
        if char in [97, 67, 260]: #A/Left
            if PlaylistListPage.page - 1 <= 0: return
            PlaylistListPage.page -= 1
            PlaylistListPage.selected = 0
        if char in [100, 68, 261]: #D/Right
            if PlaylistListPage.get_results(PlaylistListPage.page + 1).error: return
            PlaylistListPage.page += 1
            PlaylistListPage.selected = 0
        if char in [98, 66]: #B
            PlaylistEditPage.open(results[selected])
            
        if char in [103, 71, 330]: #G/Del
            try: playlist = results[selected]
            except IndexError: return
            
            PlaylistListPage.selected = 0
            playlistsdb.delete(playlist)
            
        if char in [102, 70]: #F
            if PlaylistListPage.db != playlistsdb:
                PlaylistListPage.db = playlistsdb
                return
            
            query = simpledialog.askstring("Search", "Prompt")
            if query == None: return

            searchdb = item(content=[])
            PlaylistListPage.db = searchdb
            
            for p in playlistsdb.content:
                if query.lower() in p.name.lower(): searchdb.content.append(p)
            
        if char in [120, 88]: #X            
            SongsPage.select = item(mode=True, output = [], return_page = PlaylistListPage, callback = PlaylistListPage.create_playlist_callback)
            current.page = SongsPage
        
        if char in [99, 67]: #C
            msgpage("Feature unavailable", PlaylistListPage)
            
        if char == 32: #Space
            PlaylistPage.open(results[selected])
        if char in [10, 459]: #Enter
            songs = []
            for song in results[selected].songs:
                song = songsdb.find("path", song)
                if song != None: songs.append( song )
                
            if len(songs) == 0:
                message("Unable to play: playlist is empty")
                return
                
            if config.musicShuffle: random.shuffle(songs)
            MusicPlayerPage.queue_index = 0
            MusicPlayerPage.queue = songs
            MusicPlayerPage.playsong(songs[0].path)
            if config.playerOnSelect: current.page = MusicPlayerPage
            
    def create_playlist_callback(songs):
        if len(songs) == 0:
            message("Cancelled")
            return
        
        name = simpledialog.askstring("AudioWave", "Playlist name")
        if name in [None, ""]: name = "Unknown Playlist"
        
        song_paths = []
        for s in songs:
            song_paths.append(s.path)
        
        p = db.Item(name=name, songs=song_paths)
        playlistsdb.add(p)
    
class WelcomePage:
    def render(sc):
        msg1 = "Welcome to AudioWave"
        msg2 = "Press E to open music player"
        sc.addstr(centerY(), centerX(msg1), msg1)
        sc.addstr(centerY()+1, centerX(msg2), msg2)
    
    def process_key(char): pass
        
class KeybindsPage:
    index = 0
    
    musicplayer = item(name="Music Player",
        keybinds = [
            item(key="Space", desc="Pause/resume"),
            item(key="UP", desc="Volume up"),
            item(key="DOWN", desc="Volume down"),
            item(key="LEFT", desc="Previous song"),
            item(key="RIGHT", desc="Next song"),
            item(key="A", desc="Go forwards"),
            item(key="D", desc="Go backwards"),
            
        ])
    settings = item(name="Settings",
        keybinds = [
            item(key="UP", desc="Move selection up"),
            item(key="DOWN", desc="Move selection down"),
            item(key="LEFT", desc="Number decrease"),
            item(key="RIGTH", desc="Number increase"),
            item(key="Enter", desc="Change boolean/press button"),       
        ])
    songs = item(name="Song list",
        keybinds = [
            item(key="UP", desc="Move selection up"),
            item(key="DOWN", desc="Move selection down"),
            item(key="Enter", desc="Play song"),
            item(key="Space", desc="Add song to queue"),
            item(key="D/RIGHT", desc="Next page"),
            item(key="A/LEFT", desc="Previous page"),
            item(key="G/DEL", desc="Delete song"),
            item(key="B", desc="Edit song details"),
            item(key="X", desc="Add song"),
            item(key="C", desc="Add song from youtube"),
            item(key="F", desc="Search/Close search results")
        ])
    playlists = item(name="Playlist list",
        keybinds = [
            item(key="UP", desc="Move selection up"),
            item(key="DOWN", desc="Move selection down"),
            item(key="Enter", desc="Play playlist"),
            item(key="Space", desc="Open playlist"),
            item(key="D/RIGHT", desc="Next page"),
            item(key="A/LEFT", desc="Previous page"),
            item(key="G/DEL", desc="Delete playlist"),
            item(key="B", desc="Edit playlist details"),
            item(key="X", desc="Create playlist"),
            item(key="F", desc="Search/Close search results"),
            
        ])
    playlistinfo = item(name="Playlist view",
        keybinds = [
            item(key="UP", desc="Move selection up"),
            item(key="DOWN", desc="Move selection down"),
            item(key="Enter", desc="Play song"),
            item(key="D/RIGHT", desc="Next page"),
            item(key="A/LEFT", desc="Previous page"),
            item(key="G/DEL", desc="Remove song from playlist"),
            item(key="B", desc="Edit song details"),
            item(key="X", desc="Edit playlist"),
        ])
    pages = [musicplayer, settings, songs, playlists, playlistinfo]
    
    def render(sc):
        
        page = KeybindsPage.pages[KeybindsPage.index]
        
        controls = "[A] Previous page   [D] Next page"
        sc.addstr(config.screenY-1, centerX(controls), controls)
        
        x_offset = 5
        for x in KeybindsPage.pages:
            if x == page: sc.addstr(4,x_offset, x.name, curses.A_REVERSE)
            else: sc.addstr(4,x_offset, x.name)
            x_offset += len(x.name)+2
        
        for x in range(len(page.keybinds)):
            i = page.keybinds[x]
            sc.addstr(6+x, 5, f"[{i.key}] {i.desc}")
    
    def process_key(char):
        if char in [97, 67, 260]: #A/Left
            if KeybindsPage.index - 1 < 0:
                KeybindsPage.index = len(KeybindsPage.pages) - 1
            else: KeybindsPage.index -= 1

        if char in [100, 68, 261]: #D/Right
            if KeybindsPage.index + 1 >= len(KeybindsPage.pages):
                KeybindsPage.index = 0
            else: KeybindsPage.index += 1

class SongEditPage:
    song = item(title="Unknown Title", artist="Unknown Artist", album="Unknown Album", path="No path")
    options = [
        item(value=song.title, attr="title"),
        item(value=song.artist, attr="artist"),
        item(value=song.album, attr="album"),
        item(value=song.path, attr="path"),
    ]
    selected = 0
    
    def open(song):
        SongEditPage.song = song
        SongEditPage.options = [
            item(value=song.title, attr="title"),
            item(value=song.artist, attr="artist"),
            item(value=song.album, attr="album"),
            item(value=song.path, attr="path"),
        ]
        current.page = SongEditPage
    
    def render(sc):    
        controls = "[Enter] Edit   [ESC] Return"
        sc.addstr(config.screenY-1, centerX(controls), controls)
        
        sc.addstr(4,5, "TITLE  ", curses.A_REVERSE)
        sc.addstr(5,5, "ARTIST ", curses.A_REVERSE)
        sc.addstr(6,5, "ALBUM  ", curses.A_REVERSE)
        sc.addstr(7,5, "PATH   ", curses.A_REVERSE)
        
        for x in range(len(SongEditPage.options)):
            if SongEditPage.selected == x: sc.addstr(4+x, 13, str(SongEditPage.options[x].value), curses.A_REVERSE)
            else: sc.addstr(4+x, 13, str(SongEditPage.options[x].value))
        
        
        
    def process_key(char):
        if SongEditPage.song == None:
            current.page = SongsPage
            return
        
        if char == 259: #down
            if SongEditPage.selected - 1 < 0: return
            SongEditPage.selected -= 1 
        if char == 258: #up
            if SongEditPage.selected + 1 > len(SongEditPage.options)-1: return
            SongEditPage.selected += 1
        if char in [10, 459]: #enter
            selected = SongEditPage.options[SongEditPage.selected]
            new_val = simpledialog.askstring("AudioWave", selected.attr)
            if new_val == None:
                message("Cancelled")
                return
            song = songsdb.find("path", SongEditPage.song.path)
            setattr(song, selected.attr, new_val)
            SongEditPage.open(song)
        if char in [27]: #escape
            current.page = SongsPage        

class InfoPage:
    def render(sc):
        sc.addstr(5,5, "DEVELOPER", curses.A_REVERSE)
        sc.addstr(5,25, "Xellu")
        
        sc.addstr(6,5, "GITHUB", curses.A_REVERSE)
        sc.addstr(6,25, "https://github.com/xellu/audiowave")
        
        sc.addstr(7,5, "VERSION", curses.A_REVERSE)
        sc.addstr(7,25, version)
    

    def process_key(char):
        current.page = SettingsPage

class ExitPage:
    def render(sc):
        if not config.exitPrompt:
            save()
            os._exit(0)
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
        category("Playlists", "T", [116, 84],PlaylistListPage),
        category("Settings", "S", [115, 83], SettingsPage),
        category("Exit", "Q", [113, 81], ExitPage)
    ]

#----

def save():
    songsdb.save()
    playlistsdb.save()
    config.save()
    MusicPlayerPage.action = item(action="exit")
    
    render.deactivate()

render = render_engine()
listener = keylistener_engine()

threading.Thread(target=render.start).start()
threading.Thread(target=listener.start).start()
threading.Thread(target=MusicPlayerPage.play).start()
threading.Thread(target=MusicPlayerPage.loop_thread).start()



rpc = discordrpc.Presence(1140567681309880441)

try:
    rpc.connect()
    RPCCon = True
except:
    RPCcon = False
    
while True:
    try:
        time.sleep(5)
        if RPCCon:
            rpc.update()
    except KeyboardInterrupt:
        save()
        print("Exiting...")
        os._exit(0)
    except Exception as error:
        save()
        print(f"Application crashed: {error}")
        os._exit(0)