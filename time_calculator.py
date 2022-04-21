"""Time duration calculator

This script was build for django program where calculate rent duration.
Its calculate only time when rent house is open from 9 to 16.
Max duration of rents is 7 days

Script give free 15 minutes customer, so from duration script remove 15 min.
If you want exactly duration call before  getTotalTime/getTotalTimeHumanFormat this funciton updateCleanTime


Calling outputs:
    * getTotalTime - returns duration in minutes (for storaging in database)
    * getTotalTimeHumanFormat - return duration string in Slovak language  (for simple showing user)
"""


import datetime
import pytz
from django.utils import timezone

utc = pytz.UTC

END_DAY_HOUR = 16
START_DAY_HOUR = 9
GRATIS = 15
DAY = 7
HOUR = 60


class TimeCalculator:
    """"
    HOURS and MINUTES are calculated for future storage as DATETIME

    convert table:
    1h  60
    2h  120
    3h  180
    4h  240
    5h  300
    6h  360
    7h  420

    """

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time if end_time is not None else timezone.now()

        self.counter_days = 0
        self.complet_minutes = 0
        self.total_time = 0
        self.run()


    def getTotalTimeHumanFormat(self):
        left = self.total_time

        day = left // (HOUR * DAY)
        left -= day * (HOUR * DAY)

        hours = left // HOUR
        left -= hours * HOUR

        minutes = left

        result = ""
        if day > 0:
            result += "{} Dni ".format(day)
        if hours > 0:
            result += "{}H ".format(hours)
        result += "{}M".format(minutes)
        return result

    def calculateOneDay(self):
        total = self.end_time - self.start_time
        self.complet_minutes = int(total.seconds / HOUR)

    def calculateFirstDay(self):
        minute = 0
        if self.start_time.hour > END_DAY_HOUR:
            hours = 0
        else:
            hours = END_DAY_HOUR - self.start_time.hour
            minute = self.start_time.minute

        self.complet_minutes = (hours * HOUR) - minute

    def calculateLasttDay(self):
        minute = 0
        if self.end_time.hour < START_DAY_HOUR:
            hours = 0
        else:
            hours = self.end_time.hour - START_DAY_HOUR
            minute = self.end_time.minute
        self.complet_minutes += (hours * HOUR) + minute

    def calculateOthertDay(self):
        range = self.end_time.day - self.start_time.day
        if (range) > 1:
            self.counter_days = range - 1

    def run(self):

        if self.end_time.day == self.start_time.day:
            self.calculateOneDay()
        else:
            self.calculateFirstDay()
            self.calculateLasttDay()
            self.calculateOthertDay()

        self.calculateTime()

    def calculateTime(self):
        self.total_time = self.complet_minutes + (self.counter_days * DAY * HOUR)
        if self.total_time <= GRATIS:
            self.total_time = 0
        else:
            self.total_time -= GRATIS

    def getTotalTime(self):
        return self.total_time

    def updateCleanTime(self):
        self.total_time = self.complet_minutes + (self.counter_days * DAY * HOUR)


if __name__ == '__main__':
    start = datetime.datetime.strptime("2019-10-09 9:00:00", "%Y-%m-%d %H:%M:%S")      #SET YOUR START TIME
    end = datetime.datetime.strptime("2019-10-16 16:00:00", "%Y-%m-%d %H:%M:%S")        #SET YOUR END TIME
    t = TimeCalculator(start, end)
    time_range = t.getTotalTime()
    time_range_human = t.getTotalTimeHumanFormat()

    print(f"time_range {time_range}")
    print(f"time_range_human {time_range_human}")
