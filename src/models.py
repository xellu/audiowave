from dataforge import console

class SettingInt:
    def __init__(self, max, min, step, value = None):
        self.value = value
        self.max = max
        self.min = min
        self.step = step
        
class SettingStr:
    def __init__(self, max_len, value = None):
        self.value = value
        self.max_len = max_len
        
class SettingBool:
    def __init__(self, value = None):
        self.value = True if value else False
        
class SettingEnum:
    def __init__(self, options, value = None):
        self.value = value
        self.options = options
        
class Setting:
    def __init__(self, name, description, setting, config, attr, dict_key = None, component = None, callback = None):
        """
        Setting Wrapper Class
        
        Args:
            name (str): The name of the setting
            setting (SettingInt, SettingStr, SettingBool, SettingEnum): The setting object
            config (Config): The config object
            attr (str): The attribute to set
            dict_key (str): The key in the dictionary
        """
        
        self.name = name
        self.description = description
        self.setting = setting
        self.component = component
        
        self.config = config
        self.attr = attr
        
        self.dict_key = dict_key
        self.callback = callback
        
        if self.dict_key:
            self.setting.value = getattr(self.config, self.attr).get(self.dict_key)
        else:
            self.setting.value = getattr(self.config, self.attr)
        
    def refresh(self):
        if self.dict_key:
            self.setting.value = getattr(self.config, self.attr).get(self.dict_key)
        else:
            self.setting.value = getattr(self.config, self.attr)
        
    def get(self):
        if self.dict_key:
            return getattr(self.config, self.attr).get(self.dict_key)
        
        return self.setting.value
    
    def set(self):
        if self.dict_key:
            getattr(self.config, self.attr)[self.dict_key] = self.setting.value
        else:
            setattr(self.config, self.attr, self.setting.value)
            
        self.config.save()
        console.info(f"Updated config.{self.attr}{f'[{self.dict_key}]' if self.dict_key else ''} = {self.setting.value} ({type(self.setting).__name__})")
        
        if self.callback:
            self.callback()