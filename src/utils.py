from photon.theme import Colors, Theme

def get_config_theme():
    from .core import Config

    colors = vars(Colors).items()
    colors =  {name: value for name, value in colors if name.isupper()}

    theme = {}

    for c in ["primary", "success", "warning", "error"]:
        theme[c] = get_config_color(Config, colors, c)
        
    return Theme(**theme)


def get_config_color(config, colors,key):
    default = {
        "primary": Colors.RED,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED
    }
    
    theme = config.Theme
    if theme.get(key) is None:
        return default[key]
    
    return colors[theme[key]]