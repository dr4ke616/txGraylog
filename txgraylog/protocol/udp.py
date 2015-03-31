# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: udp
    :platform: Unix, Windows
    :synopsis: Graylog UDP protocol
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from collections import deque
from socket import gethostname

from gelf import GelfProtocol
from twisted.internet import protocol, reactor


class UDPPlainTextProtocol(protocol.DatagramProtocol):
    """ Plain Text protocol which generates and sends raw text
        data to a Graylog2 server
    """

    parameter_override = {}

    def __init__(self, host, port):
        """ Initialize our protocol
        """
        self.host = host
        self.port = port

        self.resolved = False
        self.started = False
        self.connected = False
        self.host_address = None

        self.hostname = gethostname()
        self.buffer = deque(maxlen=1000)

        reactor.callWhenRunning(self.resolve)

    def connect(self):
        """ Connect our UDP socket.We do this so that we can accept a hostname
            as the host parameter without becoming incredibly slow due to DNS
            lookups on each send
        """
        if self.resolved and self.started and not self.connected:
            self.transport.connect(self.host_address, self.port)
            self.connected = True

            while True:
                try:
                    event = self.buffer.pop()
                    self.send_to_graylog(event)
                except IndexError:
                    break

    def resolve(self):
        """ Resolve the host IP address to avoid to many DNS queries
        """
        d = reactor.resolve(self.host)
        d.addCallback(lambda r: setattr(self, 'host_address', r))
        d.addCallback(lambda _: setattr(self, 'resolved', True))
        d.addCallback(lambda _: self.connect())
        return d

    def startProtocol(self):
        """ Start the protocol and keep track of the state
        """
        self.started = True
        self.connect()

    def send_to_graylog(self, message):
        """ Write the data to socket
        """
        if not self.connected:
            self.buffer.append(str(message))
            return

        if self.transport:
            self.transport.write(str(message))

    def log_message(self, event):
        """ The method to be called when we want to emit a log activity
            The paramater overide can be set to include extra paramaters
        """
        event.update(self.parameter_override)
        self.send_to_graylog(event)


class UDPGelfProtocol(UDPPlainTextProtocol):
    """ Graylog Gelf protocol which generates and sends data to a
        Graylog2 server using the Gelf protocol over UDP
    """

    def log_message(self, event):
        """ The method to be called when we want to emit a log activity
            The paramater overide can be set to include extra paramaters
        """
        event.update(self.parameter_override)
        gelf = GelfProtocol(self.hostname, **event).generate()
        for message in gelf:
            self.send_to_graylog(message)
