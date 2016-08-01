from enum import Enum

class AutoNumber(Enum):
     def __new__(cls):
         value = len(cls.__members__) + 1
         obj = object.__new__(cls)
         obj._value_ = value
         return obj

class et(AutoNumber):
    ds = ()
    dht = ()
    dht_temp = ()
    dht_hum = ()
    led = ()
    pir = ()
    rs = ()
    heater = ()
    ls = ()
    ventilator = ()
    blind = ()
    switch = ()

class mt(AutoNumber):
    input   =   ()
    output  =   ()
    ambient =   ()
    led_light = ()
    
class gt(AutoNumber):
    blinds = ()
    heating = ()
    inputs = ()
    ventilation = ()
    lights  = ()
    ambient = ()

class rt(AutoNumber):
    inside = ()
    outside = ()
    kitchen = ()
    sleeping_room = ()
    wc = ()
    corridor = ()
    living_room = ()
    

class ut(AutoNumber):
    guest = ()
    inhabitant = ()
    admin = ()

class regt(AutoNumber):
    temp = ()
    hum = ()

class task_stat(AutoNumber):
    new = ()
    ready = ()
    done = ()
    logged = ()

class effect_status(AutoNumber):
    new = ()
    done = ()
