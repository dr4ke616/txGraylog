# -*- test-case-name: txGraylog.test.test_gelf -*-
# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
.. module:: gelf
    :platform: Unix, Windows
    :synopsis: Graylog2 Gelf protocol. This module is inspired by Andrew
        Snowden's own implementation of a Graylog observer. This can be
        found at https://code.launchpad.net/~andrew-snowden/txgraylog2/
.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import zlib
import time
import uuid
import struct
import jsonlib as json

from twisted.python import randbytes

IGNORE_FIELDS = set(["message", "time", "isError", "system", "id", "failure"])
WAN_CHUNK, LAN_CHUNK = 1420, 8154
GELF_LEGACY, GELF_NEW = 0, 1


class GelfProtocol(object):
    """ Gelf protocol that works with Graylog2. Each of these values
        can be passed when instantiating an instance of this class.
            {
                "version": "1.0",
                "host": "localhost",
                "short_message": "some message",
                "full_message": "some longer message",
                "timestamp": 201501011245,
                "level": 3,
                "facility": "foo",
                "_custom_value": "bar"
            }
    """

    def __init__(
            self, host, size=WAN_CHUNK, gelf_fmt=GELF_LEGACY,
            chunk=True, compress=True, **kwargs):
        """ initalise the a Gelf protocol instance.
            :param size: the size of each chunk
            :param gelf_fmt: The format of GELF chunks is changing and versions
                0.9.5p2 and before require a legacy format. This should be
                either GELF_LEGACY or GELF_NEW
            :param kwargs: `dict` containing the log paramaters to be
                used by Graylog
        """
        self.hostname = host
        self.chunk_size = size
        self.gelf_format = gelf_fmt

        self._chunk = chunk
        self._compress = compress

        self._build_log_params(kwargs)

    def generate(self):
        """ Compress the log paramaters and return either it. If
            the length of the compressed data is larger than the
            chunk size, we split into chunks
        """
        if self._chunk and len(self.encoded_log_params) > self.chunk_size:
            return list(self._get_chunks(self.encoded_log_params))
        else:
            return [self.encoded_log_params]

    def __iter__(self):
        """ Iterate over each of the log paramaters
        """
        if self._chunk and len(self.encoded_log_params) > self.chunk_size:
            return self._get_chunks(self.encoded_log_params)
        else:
            return iter(self.encoded_log_params)

    @property
    def encoded_log_params(self):
        """ Property to return back the compressed log paramaters
        """
        params = (
            zlib.compress(json.dumps(self.log_params))
            if self._compress else json.dumps(self.log_params)
        )
        return params

    def _build_log_params(self, event):
        """ Build up the log paramaters
        """
        if event['isError'] and 'failure' in event:
            level = 3
            short_message = str(event['failure'].value)
            full_message = event['failure'].getTraceback()
        else:
            level = 6
            short_message = event['message'][0] if event['message'] else ''
            full_message = ' '.join([str(m) for m in event['message']])

        self.log_params = {
            'version': event.get('version', ''),
            'host': self.hostname,
            'short_message': short_message,
            'full_message': full_message,
            'timestamp': event.get('time', time.time()),
            'level': event.get('level', level),
            'facility': event.get('system', ''),
        }

        if 'file' in event:
            self.log_params['file'] = event['file']
        if 'line' in event:
            self.log_params['line'] = event['line']

        for key, value in event.iteritems():
            if key not in IGNORE_FIELDS:
                self.log_params["_%s" % (key, )] = value

    def _get_chunks(self, compressed):
        """Split the compressed log paramaters into chunks
        """
        num_chunks = (len(compressed) / self.chunk_size) + 1

        if self.gelf_format == GELF_LEGACY:
            pieces = struct.pack('>H', num_chunks)
            chunk_id = uuid.uuid1().bytes + randbytes.secureRandom(16)

            for i in xrange(num_chunks):
                chunk = ''.join([
                    '\x1e\x0f',
                    chunk_id,
                    struct.pack('>H', i),
                    pieces,
                    compressed[
                        i * self.chunk_size:
                        i * self.chunk_size + self.chunk_size]
                    ]
                )
                yield chunk
        else:
            pieces = struct.pack('B', num_chunks)
            chunk_id = randbytes.secureRandom(8)

            for i in xrange(num_chunks):
                chunk = ''.join([
                    '\x1e\x0f',
                    chunk_id,
                    struct.pack('B', i),
                    pieces,
                    compressed[
                        i * self.chunk_size:
                        i * self.chunk_size + self.chunk_size]
                    ]
                )
                yield chunk
