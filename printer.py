from cave import User
from cooker import TwitchConnect
from welcome import opts


class Console:

    def __init__(self):
        self.user = User()
        if not self.user or opts.get("args").create:
            self.user = get_string(_("Enter your Twitch user :"))
            self.user.passwd = get_string(_("Enter your Twitch IRC oauth password :"), "oauth:")
        if not self.user.channels:
            self.user.channels = [get_string(_("Enter a channel to join :"))]
            self.user.save()

    def connect(self):
        tc = TwitchConnect(self.user.user, self.user.passwd)


def get_string(mess, prompt=""):
    return input("\n".join((mess, "".join(("> ", prompt)))))
