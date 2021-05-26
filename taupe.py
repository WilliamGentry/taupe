# To Do
# Designate tasks as being able to break up into smaller chunks
# Warning about dropped tasks
# Auto-check for rosaries, silent prayers
# Doing tasks in order
# Completing tasks / keeping track of last time habit completed
# Manually drag around and rearrange tasks
# Going to bed not-at-midnight
import csv
from datetime import datetime, timedelta
import sys
from icecream import ic
from pprint import PrettyPrinter, pformat
from functools import reduce
pp = PrettyPrinter(indent=4)

monthNum = {
    'jan': 1,
    'january': 1,
    'feb': 2,
    'february': 2,
    'mar': 3,
    'march': 3,
    'apr': 5,
    'april': 5,
    'may': 5,
    'jun': 6,
    'june': 6,
    'jul': 7,
    'july': 7,
    'aug': 8,
    'august': 8,
    'sep': 9,
    'september': 9,
    'oct': 10,
    'october': 10,
    'nov': 11,
    'november': 11,
    'dec': 12,
    'december': 12
}

startday = {"hour": 7, "minute": 0}
endday = {"hour": 22, "minute": 0}


class Task():
    def __init__(self, name, year='', month='', day='', hour=11, minute=59, length=10, priority=0):
        self.name = name
        try:
            self.year = int(year)
        except:
            self.year = datetime.now().year
        try:
            self.month = int(month)
        except:
            monthStrLowered = month.lower()
            self.month = monthNum.get(monthStrLowered, datetime.now().month)
        try:
            self.day = int(day)
        except:
            self.day = datetime.now().day
        self.time = int(hour) * 60 + int(minute)
        self.length = int(length)
        try:
            self.priority = int(priority)
        except:
            self.priority = 0

    def deadline(self):
        return self.year * 365 * 24 * 60 + self.month * 30 * 24 * 60 + self.day * 24 * 60 + self.time - self.length

    def minutesToDeadline(self):
        dt = datetime.now()
        return self.deadline() - (dt.year * 365 * 24 * 60 + dt.month * 30 * 24 * 60 + dt.day * 24 * 60 + dt.hour * 60 + dt.minute)

    def __repr__(self):
        return pformat(self.__dict__)


class Habit():
    def __init__(self, name, earliestHour=startday["hour"], earliestMinute=startday["minute"], latestHour=endday["hour"], latestMinute=endday["minute"], length=10, priority=0):
        self.name = name
        self.earliestTime = int(earliestHour) * 60 + int(earliestMinute)
        self.latestTime = int(latestHour) * 60 + int(latestMinute)
        self.length = int(length)
        try:
            self.priority = int(priority)
        except:
            self.priority = 0

    def deadline(self):
        dt = datetime.now()
        return dt.year * 365 * 24 * 60 + dt.month * 30 * 24 * 60 + dt.day * 24 * 60 + self.latestTime - self.length

    def minutesToDeadline(self):
        dt = datetime.now()
        return self.deadline() - (dt.year * 365 * 24 * 60 + dt.month * 30 * 24 * 60 + dt.day * 24 * 60 + dt.hour * 60 + dt.minute)

    def __repr__(self):
        return pformat(self.__dict__)


class Event():
    def __init__(self, name, year="", month="", day="", startHour=0, startMinute=0, endHour=0, endMinute=0, priority=0):
        self.name = name
        try:
            self.year = int(year)
        except:
            self.year = datetime.now().year
        try:
            self.month = int(month)
        except:
            monthStrLowered = month.lower()
            self.month = monthNum.get(monthStrLowered, datetime.now().month)
        try:
            self.day = int(day)
        except:
            self.day = datetime.now().day
        self.start = int(startHour) * 60 + int(startMinute)
        self.end = int(endHour) * 60 + int(endMinute)
        try:
            self.priority = int(priority)
        except:
            self.priority = 0

    def __repr__(self):
        return pformat(self.__dict__)


def scheduleDay(tasks, habits, events, offset=0):
    if offset:
        dt = datetime(datetime.now().year, datetime.now().month, datetime.now().day) + timedelta(days=offset)
    else:
        dt = datetime.now()
    daysEvents = [event for event in events if (
        event.year == dt.year and event.month == dt.month and event.day == dt.day) and event.end >= (dt.hour * 60 + dt.minute)]
    daysEvents.sort(key=lambda x: x.start)
    daysEvents.append(Event("Bedtime", startHour=23,
                      startMinute=59, endHour=23, endMinute=59))
    moveable_todos = tasks + habits
    moveable_todos.sort(key=lambda x: (-x.priority, x.deadline()))

    time = max(startday["hour"] * 60 + startday["minute"],
                dt.hour * 60 + dt.minute)

    i = 0
    while time < endday["hour"] * 60 + endday["minute"]:
        try:
            next_event = daysEvents[i]
            time_to_next_event = next_event.start - time

        except:
            time_to_next_event = 11*60 + 59 - time

        todos_in_window = [todo for todo in moveable_todos if ((todo.length < time_to_next_event) and (
            (isinstance(todo, Habit) and todo.earliestTime <= time <= todo.latestTime) or not isinstance(todo, Habit)))]
        if todos_in_window == []:
            if time != next_event.start:
                print(
                    f"Time: {time//60 % 12 if time//60 % 12 else 12:>2}:{time%60 :0<2}\t**OPEN**")
            print(
                f"Time: {next_event.start // 60 % 12 if next_event.start // 60 % 12 else 12 :>2}:{next_event.start % 60 :0<2}\t{next_event.name}")
            i += 1
            time = next_event.end
        else:
            nearest_deadline_todo = reduce(lambda x, y: x if x.minutesToDeadline(
            ) < y.minutesToDeadline() or x.priority > y.priority else y, todos_in_window)
            print(
                f"Time: {time // 60 % 12 if time //60 % 12 else 12 :>2}:{time%60 :0>2}\t{nearest_deadline_todo.name}")
            moveable_todos.remove(nearest_deadline_todo)
            time += nearest_deadline_todo.length


tasks = []
habits = []
events = []
with open('tasks.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if row[-1] == "X":
            continue
        elif row[0] == "task":
            try:
                tasks.append(Task(*(row[1:])))
            except:
                ic(Task(*(row[1:])))
        elif row[0] == "habit":
            habits.append(Habit(*(row[1:])))
        elif row[0] == "event":
            events.append(Event(*(row[1:])))
        elif row[0] == "event_daily":
            events.append(Event(name=row[1], year=datetime.now().year, month=datetime.now(
            ).month, day=datetime.now().day, startHour=row[2], startMinute=row[3], endHour=row[4], endMinute=row[5]))
        elif row[0] == "event_weekly" and str(datetime.now().weekday()) in row[1].split():
            events.append(Event(row[2], datetime.now().year, datetime.now(
            ).month, datetime.now().day, row[3], row[4], row[5], row[6]))

try:
    scheduleDay(tasks, habits, events, int(sys.argv[1]))
except:
    scheduleDay(tasks, habits, events)