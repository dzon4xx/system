import datetime


class Clock:
    """Holds actual time. 
    Notifies about actual time
    Notifies about week day"""
    def __init__(self, ):
        self.objects_to_notify_weekday = set()
        self.objects_to_notify_time = set()

        self.now = None
        self.minute = None
        self.weekday = None

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

clock = None
