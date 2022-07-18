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
from twisted.internet.protocol import DatagramProtocol, Protocol

from txgraylog.protocol.tcp import TCPGraylogFactory


class GraylogObserver:
    """ Graylog observer
    """

    def __init__(self, protocol, host, port):
        self.protocol = protocol(host, port)

        if issubclass(self.protocol.__class__, DatagramProtocol):
            reactor.listenUDP(0, self.protocol)
        elif issubclass(self.protocol.__class__, Protocol):
            reactor.connectTCP(
                self.protocol.host,
                self.protocol.port,
                TCPGraylogFactory(self.protocol)
            )
        else:
            raise ValueError('Incompatible protocol')

    def emit(self, event_dict):
        self.protocol.log_message(event_dict)

    def start(self, with_reactor=False):
        if with_reactor:
            reactor.callWhenRunning(log.addObserver, self.emit)
        else:
            log.addObserver(self.emit)

    def stop(self):
        log.removeObserver(self.emit)
