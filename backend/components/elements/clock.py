import datetime

class Clock():
    """Holds actual time. 
    Notifies about actual time
    Notifies about week day"""
    def __init__(self, ):
        self.objects_to_notify_weekday = []
        self.objects_to_notify_time = []

        self.now = None

        self.minute = None
        self.weekday = None

    def subscribe_for_day_notification(self, who):
        self.objects_to_notify_weekday.append(who)

    def subscribe_for_minute_notification(self, who):
        self.objects_to_notify_time.append(who)


    def evaluate_time(self, ):
        self.now = datetime.datetime.now()
        
        if  self.now.minute != self.minute:
            self.minute =  self.now.minute
            for object in self.objects_to_notify_time:
                object.notify((self.now.hour, self.now.minute,))

        if self.weekday != self.now.weekday():
            self.weekday = self.now.weekday()
            for object in self.objects_to_notify_weekday:
                object.notify(self.weekday)

clock = Clock()