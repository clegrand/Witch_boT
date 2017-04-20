from itertools import count

from cave import User
from cooker import TwitchConnect, Channel
from welcome import opts, ARGS


class Console:
    KEY_QUIT = 'q'

    def __init__(self):
        self.tc = None
        self.channel = None
        self.user = User(opts[ARGS].user)
        if not self.user or opts.get(ARGS).create:
            self.user.user = get_string(_("Enter your Twitch user :"))
            self.user.passwd = get_string(_("Enter your Twitch IRC oauth password :"), "oauth:")
        if not self.user.channels:
            self.user.channels = [get_string(_("Enter a channel to join :"))]
            self.user.save()

    def connect(self):
        if len(self.user.channels) > 1:
            channel_name = menu_choice(self.user.channels, "Select the channel you want to join", self.user.channels[0])
        else:
            channel_name = self.user.channels[0]
        self.tc = TwitchConnect(self.user.user, self.user.passwd)
        self.channel = Channel(channel_name, connection=self.tc)

    def input_loop(self):
        while True:
            try:
                k = input()
            except (KeyboardInterrupt, EOFError):
                break
            if k == self.KEY_QUIT:
                break
            if self.tc:
                self.tc.send_message(k)
        self.close()

    def close(self):
        if self.tc:
            self.tc.close()


def get_string(mess, prompt=""):
    return input("\n".join((mess, "".join(("> ", prompt)))))


def menu_choice(choices, message="Select a choice", default=None):
    if not choices:
        return default

    def str_choice(number, choice):
        if isinstance(choice, (tuple, list)):
            choice = choice[1] if len(choice) > 1 else choice[0]
        return "{num} - {msg}".format(num=number, msg=choice)

    l = len(choices)
    print("{msg} [1-{num}]:".format(msg=message, num=l),
          *map(str_choice, count(1), choices),
          sep='\n')
    msg_err = "Please enter a number between 1 and {num}".format(num=l)
    while True:
        try:
            entry = input()
        except (EOFError, KeyboardInterrupt):
            return default
        try:
            entry = int(entry) - 1
        except ValueError:
            print(msg_err)
            continue
        if entry < 0:
            print(msg_err)
            continue
        try:
            elem = choices[entry]
        except IndexError:
            print(msg_err)
        else:
            if isinstance(elem, (tuple, list)):
                return elem[0]
            return elem
