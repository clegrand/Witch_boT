import re
from socket import socket
import json
import threading
from time import sleep

from lepl import Any, Regexp, Drop, Literal, Word, make_dict, FullFirstMatchException

from attic import CONNECTION_PATH
from cave import TimeLimit, parse_params
from welcome import logger


class TwitchConnect(socket):
    PASS = "PASS oauth:{}"
    USER = "NICK {}"
    CAPABILITIES = {
        "membership": "CAP REQ :twitch.tv/membership",
        "tags": "CAP REQ :twitch.tv/tags",
        "commands": "CAP REQ :twitch.tv/commands"
    }
    DEF_BUFF = 2048
    RECV_TIME = 0.1
    BEGIN_MSG = ':'
    END_MSG = '\r\n'
    DEF_MESSAGE = "{}" + END_MSG

    def __init__(self, user, passwd, conn_path=CONNECTION_PATH):
        with open(conn_path) as f:
            j = json.loads(f.read())
            c = j['irc']
            super().__init__()
            self.connect((c['host'], c['port']))
            self.send_message(self.PASS.format(passwd))
            self.send_message(self.USER.format(user))
            self.func_recv = []
            t = j.get('limit')
            if t:
                self.limit = TimeLimit(limit=t['message'], delay=t['time'])
            i = j.get('check')
            if i:
                self.check_in = i.get("in")
                if self.check_in:
                    self.check_out = i["out"]
                    self.link_func(self._ping_pong)
            self.capabilities = []
            threading.Thread(target=self._recver).start()

    def add_capabilities(self, capabilities):
        for c in capabilities:
            if c not in self.capabilities:
                self.send_message(self.CAPABILITIES[c])
                self.capabilities.append(c)

    def link_func(self, func):
        if isinstance(func, (list, tuple)):
            self.func_recv.extend(func)
        else:
            self.func_recv.append(func)

    def send_message(self, mess, check_mess=True):
        if check_mess and hasattr(self, 'limit'):
            if not self.limit.checkpoint():
                logger.warn(_("Messages number out of limit (message lost)"))
                return False
            logger.debug(self.limit)
        self.send(self.DEF_MESSAGE.format(mess).encode())
        logger.debug("< {}".format(mess))
        return True

    def _recver(self):
        while True:
            data = b''
            try:
                while not data.decode().endswith(self.END_MSG):
                    data += self.recv(self.DEF_BUFF)
                    if len(data) >= self.DEF_BUFF:
                        continue
                    break
            except OSError:
                logger.debug("Connection lost")
                return
            if data:
                logger.debug("Data : %u" % len(data))
                for d in data.decode().strip().split(self.END_MSG):
                    if d.startswith(self.BEGIN_MSG):
                        d = d[1:]
                    if d:
                        logger.info("> {}".format(d))
                        for func in self.func_recv:
                            func(d)
            else:
                return
            sleep(self.RECV_TIME)

    def _ping_pong(self, mess):
        if mess == self.check_in:
            self.send_message(self.check_out)


class Channel:
    BOT_PROMPT = "[BOT] {}"
    JOIN = "JOIN {}"
    SEND = "PRIVMSG {channel} :{msg}"
    CHANNEL_RE = {
        "user_join": re.compile(r"(?P<user>\w+)!\w+@\w+\.tmi\.twitch\.tv JOIN (?P<channel>#\w+)"),
        "get_message":
            re.compile(
                r"(?:@(?P<info>.*):|)(?P<user>\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG (?P<channel>#\w+) :(?P<message>.*)"
            ),
        "user_part": re.compile(r"(?P<user>\w+)!\w+@\w+\.tmi\.twitch\.tv PART (?P<channel>#\w+)")
    }

    def __init__(self, channel_name, connection):
        self.channel_name = "#{}".format(channel_name)
        self.connect = connection
        self.connect.send_message(self.JOIN.format(self.channel_name))
        self.connect.link_func(self._get_message)
        self.channel_plugins = []

    def link_plugins(self, func):
        if isinstance(func, (list, tuple)):
            self.channel_plugins.extend(func)
        else:
            self.channel_plugins.append(func)

    def send_message(self, message, bot_message=True):
        if bot_message:
            message = self.BOT_PROMPT.format(message)
        self.connect.send_message(self.SEND.format(
            channel=self.channel_name,
            msg=message
        ))

    def _get_message(self, msg):
        for k, r in self.CHANNEL_RE.items():
            m = r.search(msg)
            if m:
                m = m.groupdict()
                if m['channel'] == self.channel_name:
                    del m['channel']
                    i = m.get('info')
                    if i:
                        m['info'] = parse_params(i)
                    logger.debug("Match : %s with data : %s" % (k, m))
                    for f in self.channel_plugins:
                        getattr(f, k)(**m)
                    break


class ChannelPlugin:

    def __init__(self, channel):
        channel.link_plugins(self)

    def user_join(self, user, info=None):
        pass

    def get_message(self, user, message, info=None):
        pass

    def user_part(self, user, info=None):
        pass
