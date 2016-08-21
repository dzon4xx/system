import unittest
import datetime
import time

from backend.components.clock import Clock

from backend.components.tests.helper_classes import Notifiable


class TestClock(unittest.TestCase):

    def setUp(self):
        self.clock = Clock()
        self.clock.restart()

    def test_get_seconds(self):
        self.assertAlmostEqual(self.clock.get_seconds(), 0, 3)

    def test_get_milis(self):
        time.sleep(0.001)
        self.assertAlmostEqual(self.clock.get_millis(), 1, 0)

    def test_subscribe(self):

        notifiables = [Notifiable() for _ in range(3)]

        for notifiable in notifiables:
            self.clock.subscribe_for_weekday(notifiable)
            self.clock.subscribe_for_minute(notifiable)

        for notifiable in notifiables:
            self.assertIn(notifiable, self.clock.objects_to_notify_weekday)
            self.assertIn(notifiable, self.clock.objects_to_notify_time)

    def test_evaluate_time(self):

        self.clock.evaluate_time()
        self.assertEqual(self.clock.now.minute, self.clock.minute)
        self.assertEqual(self.clock.now.weekday(), self.clock.weekday)

    def test_notification(self):

        notifiable_minute = Notifiable()
        notifiable_weekday = Notifiable()

        self.clock.subscribe_for_minute(notifiable_minute)
        self.clock.subscribe_for_weekday(notifiable_weekday)

        self.clock.now = datetime.datetime.now()
        self.clock.weekday = 6

        self.clock.notify_minute()
        self.clock.notify_weekday()

        self.assertEqual(notifiable_minute.val, self.clock.now)
        self.assertEqual(notifiable_weekday.val, self.clock.weekday)

