# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: observer
    :platform: Unix, Windows
    :synopsis: The observer for which our protocols to use
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


class GraylogObserver:
    """ Graylog observer
    """

    def __init__(self, protocol, host, port):
        self.protocol = protocol(host, port)
        if type(self.protocol.__class__) == type(DatagramProtocol):
            reactor.listenUDP(0, self.protocol)

    def emit(self, event_dict):
        self.protocol.log_message(event_dict)

    def start(self):
        log.addObserver(self.emit)

    def stop(self):
        log.removeObserver(self.emit)
