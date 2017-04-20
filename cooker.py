from socket import socket
import json
import threading
from time import sleep

from lepl import Any, Regexp, Drop, Literal, Word, make_dict, Optional, FullFirstMatchException

from attic import CONNECTION_PATH
from cave import TimeLimit
from welcome import logger


class TwitchConnect(socket):
    PASS = "PASS oauth:{}"
    USER = "NICK {}"
    DEF_BUFF = 1024
    RECV_TIME = 0.1
    DEF_MESSAGE = "{}\r\n"

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
            threading.Thread(target=self._recver).start()

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
        p = Optional(~Literal(':')) & Any()[:, ...] & ~Regexp("\r\n")
        while True:
            data = self.recv(self.DEF_BUFF)
            if data:
                r = p.parse(data.decode())[0]
                if r:
                    logger.info("> {}".format(r))
                    for func in self.func_recv:
                        func(r)
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

    def send_message(self, message):
        self.connect.send_message(self.SEND.format(
            channel=self.channel_name,
            msg=self.BOT_PROMPT.format(message)
        ))

    def _get_message(self, msg):
        user = Word() > "user"
        message = Any()[..., ] > "response"
        get_msg = user & Drop(
            Literal('!') &
            user &
            Literal('@') &
            user &
            Regexp(r"\.tmi\.twitch\.tv PRIVMSG ") &
            self.channel_name &
            Regexp(r" :")
        ) & message > make_dict
        try:
            msg = get_msg.parse(msg)[0]
        except FullFirstMatchException:
            return
        logger.debug("{user}: {response}".format(**msg))
