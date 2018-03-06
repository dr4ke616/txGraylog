# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: tcp
    :platform: Unix, Windows
    :synopsis: Graylog TCP protocol
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from collections import deque
from socket import gethostname

from twisted.internet.protocol import Protocol, ReconnectingClientFactory

from gelf import GelfProtocol


class TCPPlainTextProtocol(Protocol):
    """ Plain Text protocol which generates and sends raw text
        data to a Graylog2 server
    """

    parameter_override = {}

    def __init__(self, host, port):
        """ Initialize our protocol
        """
        self.host = host
        self.port = port

        self.connected = False

        self.hostname = gethostname()
        self.buffer = deque(maxlen=1000)

    def connectionMade(self):
        """ Connection made to Graylog server
        """
        self.connected = True

        while True:
            try:
                event = self.buffer.pop()
                self.send_to_graylog(event)
            except IndexError:
                break

    def connectionLost(self, reason):
        """ Connection lost to Graylog server
        """
        self.connected = False

    def send_to_graylog(self, message):
        """ Write the data to socket
        """
        message = str(message)
        if not message.endswith('\x00'):
            message += '\x00'

        if not self.connected:
            self.buffer.append(message)
            return

        self.transport.write(message)

    def log_message(self, event):
        """ The method to be called when we want to emit a log activity
            The paramater overide can be set to include extra paramaters
        """
        event.update(self.parameter_override)
        self.send_to_graylog(event)


class TCPGelfProtocol(TCPPlainTextProtocol):
    """ Graylog Gelf protocol which generates and sends data to a
        Graylog2 server using the Gelf protocol over TCP
    """

    def log_message(self, event):
        """ The method to be called when we want to emit a log activity
            The paramater overide can be set to include extra paramaters
        """
        event.update(self.parameter_override)
        gelf = GelfProtocol(
            self.hostname, chunk=False, compress=False, **event).generate()
        for message in gelf:
            self.send_to_graylog(message)


class TCPGraylogFactory(ReconnectingClientFactory):

    def __init__(self, protocol):
        self.protocol = protocol

    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(
            self, connector, reason
        )

    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason
        )

    def buildProtocol(self, addr):
        self.resetDelay()
        return self.protocol
