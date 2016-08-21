import datetime
import time


class Clock:
    """Holds actual time. 
    Notifies about actual time
    Notifies about week day"""

    _is_initialized = False
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, ):
        if not Clock._is_initialized:
            Clock._is_initialized = True
            self.objects_to_notify_weekday = set()
            self.objects_to_notify_time = set()

            self.now = None
            self.minute = None
            self.weekday = None

            self.system_start = time.time()

    def subscribe_for_weekday(self, who):
        self.objects_to_notify_weekday.add(who)

    def subscribe_for_minute(self, who):
        self.objects_to_notify_time.add(who)

    def notify_minute(self):
        self.minute = self.now.minute
        for _object in self.objects_to_notify_time:
            _object.notify(self.now)

    def notify_weekday(self):
        self.weekday = self.now.weekday()
        for _object in self.objects_to_notify_weekday:
            _object.notify(self.weekday)

    def evaluate_time(self, ):
        """Evaluates current time. If minutes or day changes it notifies related objects"""
        self.now = datetime.datetime.now()
        
        if self.now.minute != self.minute:
            self.notify_minute()

        if self.weekday != self.now.weekday():
            self.notify_weekday()

    def get_seconds(self):
        return time.time() - self.system_start

    def get_millis(self):
        return (time.time() - self.system_start)*1000

    def restart(self):
        self.system_start = time.time()
