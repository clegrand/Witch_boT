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
        self.tc = TwitchConnect(self.user.user, self.user.passwd)
        self.channel = Channel(self.user.channels[0], self.tc)

    def input_loop(self):
        while True:
            k = input()
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
