# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: service
    :platform: Unix, Windows
    :synopsis: The service for which our Graylog protocol can use
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from twisted.application import service

from txgraylog.observer import GraylogObserver


class GraylogService(service.Service):
    """ Graylog Service that will be started by twisted
    """

    def __init__(self, protocol, host, port):
        self.observer = GraylogObserver(protocol, host, port)

    def startService(self):
        service.Service.startService(self)
        self.observer.start()

    def stopService(self):
        service.Service.stopService(self)
        self.observer.stop()
