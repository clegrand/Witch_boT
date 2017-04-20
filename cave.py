import json
import time

from functools import partial
from itertools import filterfalse

from attic import USER_PATH


class User:

    def __init__(self, user=None, filename=USER_PATH):
        self.user_file = filename
        try:
            with open(filename) as f:
                j = json.loads(f.read())
                self.user = j['user'] or user
                self.passwd = j['pass']
                self.channels = j.get('channel', [])
        except FileNotFoundError:
            self.user = None
            self.passwd = None
            self.channels = []

    def save(self, filename=None):
        if not filename:
            filename = self.user_file
        with open(filename, "w") as f:
            j = {
                'user': self.user,
                'pass': self.passwd,
                'channel': self.channels
            }
            f.write(json.dumps(j, indent=2))

    def __bool__(self):
        return bool(self.user and self.passwd)


class TimeLimit:

    def __init__(self, limit, delay=1.0):
        self._times = []
        self.limit = limit
        self.delay = delay  # In seconds

    def _refresh(func):  # Decorator
        def wrapper(inst, *args, **kwargs):
            inst.refresh()
            return func(inst, *args, **kwargs)
        return wrapper

    @_refresh
    def checkpoint(self):
        if self:
            self._times.append(time.perf_counter())
            return True
        return False

    def refresh(self):
        self._times = list(filterfalse(partial(self._out_of_limit, time_limit=self.delay), self._times))

    @staticmethod
    def _out_of_limit(elem, time_limit):
        return (time.perf_counter() - elem) > time_limit

    @_refresh
    def __repr__(self):
        return "{cur}/{max} {delay}s".format(
            cur=len(self._times),
            max=self.limit,
            delay=self.delay
        )

    @_refresh
    def __bool__(self):
        return self._times.__len__() < self.limit


def parse_params(msg):
    d = {}
    for m in msg.split(';'):
        f = m.find('=')
        d[m[:f]] = m[f+1:]
    return d
