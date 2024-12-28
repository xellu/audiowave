import photon
from photon.components import *
from photon.theme import Variants

from ..core import Config
from ..models import Setting, SettingBool, SettingEnum, SettingInt, SettingStr
from ..utils import get_config_theme

from ..player import Player

class Settings(photon.Page):
    def __init__(self, app):
        self.app = app
        
        self.pages = {
            "current": 0,
            "pages": [
                "General",
                "Appearance",
                "About"
            ]
        }
        
        self.str_setting_input = {
            "open": False,
            "value": "",
            "callback": None,
            "component": Input(
                app = self.app,
                title = "Enter Value",
                variant = Variants.PRIMARY,
                auto_render = False
            )
        }
        
        self.settings = {
            "General": [
                Setting(
                    name = "Volume", description = "The volume of the audio player", callback = lambda: Player.set_volume(Config.Volume),
                    setting = SettingInt(100, 0, 1),
                    component = Slider(app, max = 100, width = 40,
                        char_pre = "█", char_post = "▒", char_point="█",
                        auto_render = False
                    ),
                    config = Config, attr = "Volume"
                )    
            ],
            "Appearance": [
                #SCREEN DIMENSIONS
                Setting(
                    name = "Window Width", description = "The width of the screen (NOTICE: May cause visual issues if not set properly)", callback=self.update_screen,
                    setting = SettingInt(512, 120, 1),
                    component = Slider(app, max = 512, width = 40,
                        char_pre = "█", char_post = "▒", char_point="█",
                        auto_render = False
                    ),
                    config = Config, attr = "ScreenX"
                ),
                Setting(
                    name = "Window Height", description = "The height of the screen (NOTICE: May cause visual issues if not set properly)", callback=self.update_screen,
                    setting = SettingInt(512, 25, 1),
                    component = Slider(app, max = 512, width = 40,
                        char_pre = "█", char_post = "▒", char_point="█",
                        auto_render = False
                    ),
                    config = Config, attr = "ScreenY"
                ),
                
                #THEME
                Setting(
                    name = "Primary Color", description = "The primary color of the app", callback=self.update_theme,
                    setting = SettingEnum(["WHITE", "BLACK", "RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN"]),
                    config = Config, attr = "Theme", dict_key = "primary"
                ),
                Setting(
                    name = "Success Color", description = "The color for success messages", callback=self.update_theme,
                    setting = SettingEnum(["WHITE", "BLACK", "RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN"]),
                    config = Config, attr = "Theme", dict_key = "success"
                ),
                Setting(
                    name = "Warning Color", description = "The color for warning messages", callback=self.update_theme,
                    setting = SettingEnum(["WHITE", "BLACK", "RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN"]),
                    config = Config, attr = "Theme", dict_key = "warning"
                ),
                Setting(
                    name = "Error Color", description = "The color for error messages", callback=self.update_theme,
                    setting = SettingEnum(["WHITE", "BLACK", "RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN"]),
                    config = Config, attr = "Theme", dict_key = "error"
                ),
                
                
            ],
            "About": []
        }
        self.setting_index = 0
        
    def on_render(self, sc):
        offset = 0
        Text(self.app, x = 0, y = 1, text = " "*self.app.screenX, variant = Variants.PRIMARY, reverse = True)
        for i, page in enumerate(self.pages["pages"]):
            Text(
                app = self.app, x = offset, y = 1,
                text = f" {page} ",
                variant = Variants.PRIMARY, reverse = self.pages["current"] != i
            )
            offset += len(page)+2
        
        settings = self.settings[self.pages["pages"][self.pages["current"]]]
        for i, option in enumerate(settings):
            option.refresh()
            
            if option.component:
                option.component.y = 3+i
                option.component.reverse = self.setting_index == i        
            
            match type(option.setting).__name__:
                case "SettingBool": #slide toggle
                    Text(
                        app = self.app, x = 1, y = 3+i,
                        text = f"{option.name}:", variant = Variants.DEFAULT,
                        reverse = self.setting_index == i
                    )
                    option.component.value = option.setting.value
                    option.component.x = len(option.name) + 3
                    option.component.on_render(sc)
                
                case "SettingInt": #slider
                    label = f"{option.name}: {str(option.setting.value).rjust(len(str(option.setting.max)))} "
                    Text(
                        app = self.app, x = 1, y = 3+i,
                        text = label, variant = Variants.DEFAULT,
                        reverse = self.setting_index == i
                    )
                    option.component.value = option.setting.value
                    option.component.x = len(label) + 1
                    option.component.on_render(sc)
                    
                case "SettingStr": #none
                    Text(
                        app = self.app, x = 1, y = 3+i,
                        text = f"{option.name}: {option.setting.value}", variant = Variants.DEFAULT,
                        reverse = self.setting_index == i
                    )
                    
                case "SettingEnum": #none
                    Text(
                        app = self.app, x = 1, y = 3+i,
                        text = f"{option.name}: [{option.setting.value}]", variant = Variants.DEFAULT,
                        reverse = self.setting_index == i
                    )
                    
                case _: #fallback
                    Text(
                        app = self.app, x = 1, y = 3+i,
                        text = f"UNKNOWN SETTING TYPE: {type(option.setting).__name__}", variant = Variants.ERROR, reverse = self.setting_index == i
                    )
             
            if self.setting_index == i:       
                Text(
                    app = self.app, variant = Variants.PRIMARY,
                    text = f"{option.name} - {option.description}",
                    x = 1, y = self.app.screenY - 4,
                )
            
        if self.str_setting_input["open"]:
            self.str_setting_input["component"].on_render(sc)    
                
            
    def on_input(self, key):
        char = photon.keymap.get_key(key)
        
        if self.str_setting_input["open"]:
            self.str_setting_input["component"].on_input(key)
            return
        
        if char.lower() == "d" or char == "tab":
            self.pages["current"] += 1
            if self.pages["current"] >= len(self.pages["pages"]):
                self.pages["current"] = 0
            
            self.setting_index = 0
            return
                
        if char.lower() == "a":
            self.pages["current"] -= 1
            if self.pages["current"] < 0:
                self.pages["current"] = len(self.pages["pages"]) - 1
                
            self.setting_index = 0
            return
        
        if char == "up":
            self.setting_index -= 1
            if self.setting_index < 0:
                self.setting_index = len(self.settings[self.pages["pages"][self.pages["current"]]]) - 1
            return
        
        if char == "down":
            self.setting_index += 1
            if self.setting_index >= len(self.settings[self.pages["pages"][self.pages["current"]]]):
                self.setting_index = 0
                
            return
        
        
        #process setting input
        settings = self.settings[self.pages["pages"][self.pages["current"]]]
        option = settings[self.setting_index]
        match type(option.setting).__name__:
            
            #boolean
            case "SettingBool":
                if char in ["space", "enter", "left", "right"]:
                    option.setting.value = not option.setting.value
                    option.set()
                    return
                
            #integer
            case "SettingInt":
                if char == "left":
                    option.setting.value -= 1
                    if option.setting.value < option.setting.min:
                        option.setting.value = option.setting.min
                    option.set()
                    return
                if char == "right":
                    option.setting.value += 1
                    if option.setting.value > option.setting.max:
                        option.setting.value = option.setting.max
                    option.set()
                    return
               
            #string 
            case "SettingStr":
                if char in ["space", "enter"]:
                    def option_callback(value): #i really love nesting shit huh
                        option.setting.value = value #or i just have down syndrome idk
                        option.set()
                        self.str_setting_input["open"] = False
                        self.str_setting_input["value"] = ""
                        self.str_setting_input["callback"] = None
                    
                    self.str_setting_input["open"] = True
                    self.str_setting_input["value"] = option.setting.value
                    self.str_setting_input["callback"] = option_callback
                    self.str_setting_input["component"].value = option.setting.value
                    return
                
            #enum
            case "SettingEnum":
                if char in ["right", "enter"]:
                    index = option.setting.options.index(option.setting.value)
                    index += 1
                    if index >= len(option.setting.options):
                        index = 0
                        
                    option.setting.value = option.setting.options[index]
                    option.set()
                    
                if char == "left":
                    index = option.setting.options.index(option.setting.value)
                    index -= 1
                    if index < 0:
                        index = len(option.setting.options) - 1
                        
                    option.setting.value = option.setting.options[index]
                    option.set()
                    
                    
    def update_screen(self):
        self.app.screenX = Config.ScreenX
        self.app.screenY = Config.ScreenY
        
    def update_theme(self):
        theme = get_config_theme()
        theme.apply()
        self.app.theme = theme