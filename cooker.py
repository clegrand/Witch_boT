from socket import socket
import json
import threading
from time import sleep

from lepl import Any, Regexp

from attic import CONNECTION_PATH
from welcome import logger


class TwitchConnect(socket):
    PASS = "PASS oauth:{}"
    USER = "NICK {}"
    DEF_BUFF = 1024
    RECV_TIME = 0.1

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
                self.message_ratio = t['message'] / t['time']
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

    def send_message(self, mess):
        def_message = "{}\r\n"
        self.send(def_message.format(mess).encode())
        logger.debug("< {}".format(mess))

    def _recver(self):
        p = Any()[:, ...] & ~Regexp("\r\n")
        while True:
            r = p.parse(self.recv(self.DEF_BUFF).decode())[0]
            if r:
                logger.info("> {}".format(r))
                for func in self.func_recv:
                    func(r)
            sleep(self.RECV_TIME)

    def _ping_pong(self, mess):
        if mess == self.check_in:
            self.send_message(self.check_out)
