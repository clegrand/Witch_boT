import json

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
