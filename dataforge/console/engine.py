import time as _time

def time(Format):
    return _time.strftime(Format, _time.localtime())

