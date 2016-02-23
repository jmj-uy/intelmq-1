# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os.path 
import sys 

from intelmq.lib.bot import Bot 
from intelmq.lib.message import Report

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout


class XMPPListener(ClientXMPP):
    """ 
        XMPP Listener class to handle the messages received from XMPP
    """
    def __init__(self, bot, jid, password, room):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("groupchat_message", self.muc_message)

        self.jid = jid
        self.room = room
        self.bot = bot
        self.nick = self.bot.bot_id


    def muc_message(self, msg):
        report = Report()
        report.add("raw", msg['body'])
        report.add("feed.name", self.bot.parameters.feed)
        report.add("feed.accuracy", self.bot.parameters.accuracy)
        self.bot.send_message(report)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        self.plugin['xep_0045'].joinMUC(self.room,
                                    self.nick,
                                    wait=True)


class XMPPCollectorBot(Bot):
    """ Main class for the XMPP protocol collector """

    def init(self):
        self.jid = getattr(self.parameters, 'jid', 'intelmq@localhost')
        self.password = getattr(self.parameters, 'password', '')
        self.room = getattr(self.parameters, 'room', 'intelmq@conferences.localhost')
        self.use_tls = getattr(self.parameters, 'use_tls', True)
        self.use_ssl = getattr(self.parameters, 'use_ssl', False)
        self.server = getattr(self.parameters, 'server', None)
        self.port = getattr(self.parameters, 'port', None)

        self.xmpp = XMPPListener(self, self.jid, self.password, self.room)
        self.xmpp.register_plugin('xep_0045')
        self.xmpp.connect(address=(self.server, self.port), use_tls=self.use_tls, use_ssl=self.use_ssl)
        self.xmpp.process(block=False)


    def disconnect(self):
        self.xmpp.disconnect(wait=True)

    def process(self):
        pass

if __name__ == "__main__":
    bot = XMPPCollectorBot(sys.argv[1])
    bot.start()

