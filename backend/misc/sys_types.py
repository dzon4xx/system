from enum import Enum


class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class Et(AutoNumber):
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


class Mt(AutoNumber):
    input = ()
    output = ()
    ambient = ()
    led_light = ()


class Gt(AutoNumber):
    blinds = ()
    heating = ()
    inputs = ()
    ventilation = ()
    lights = ()
    ambient = ()


class Rt(AutoNumber):
    inside = ()
    outside = ()
    kitchen = ()
    sleeping_room = ()
    wc = ()
    corridor = ()
    living_room = ()
    

class Ut(AutoNumber):
    guest = ()
    inhabitant = ()
    admin = ()


class Regt(AutoNumber):
    temp = ()
    hum = ()


class TaskStat(AutoNumber):
    new = ()
    ready = ()
    done = ()
    logged = ()


class EffectStatus(AutoNumber):
    new = ()
    done = ()
