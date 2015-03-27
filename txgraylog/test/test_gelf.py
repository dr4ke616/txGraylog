# Copyright (c) 2015 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for more details

"""
Tests for :class: `~txgraylog.gelf.Graylog2`
"""
import time
import json
import zlib
import struct
import binascii

from twisted.trial import unittest
from twisted.python import failure, randbytes

from txgraylog.gelf import GelfProtocol


class TestGELF(unittest.TestCase):
    """ Test our conversion between event dictionaries and GELF messages
    """

    def testStandardLog(self):
        """ Test a standard event dictionary that would be passed in by Twisted
        """
        t = time.time()
        g = GelfProtocol('localhost', **{
            'system': 'protocol',
            'message': ['this is a log message', 'which could be continued'],
            'isError': False,
            'version': '1.0',
            'time': t
        })

        self.assertEquals(len(g.generate()), 1)

        params = json.loads(zlib.decompress(g.generate()[0]))

        self.assertEquals(params['facility'], 'protocol')
        self.assertEquals(params['short_message'], 'this is a log message')
        self.assertEquals(
            params['full_message'],
            'this is a log message' + ' which could be continued'
        )
        self.assertEquals(params['level'], 6)
        self.assertEquals(params['version'], '1.0')
        self.assertEquals(params['timestamp'], t)

    def testExtendedParamaters(self):
        """
        Test a log message with arbitrary parameters
        """

        g = GelfProtocol('localhost', **{
            'system': 'protocol',
            'message': ['this is a log message'],
            'isError': False,
            'time': time.time(),
            'username': 'foo',
            'bar': 'baz'
        })

        params = json.loads(zlib.decompress(g.generate()[0]))

        self.assertEquals(params['_username'], 'foo')
        self.assertEquals(params['_bar'], 'baz')

    def testErrorLog(self):
        """
        Test an error log
        """

        f = failure.Failure(Exception('foo'))
        g = GelfProtocol('localhost', **{
            'system': 'protocol',
            'failure': f,
            'isError': True,
            'time': time.time(),
        })

        params = json.loads(zlib.decompress(g.generate()[0]))

        self.assertEquals(params['level'], 3)
        self.assertEquals(params['short_message'], 'foo')
        self.failUnless('Traceback' in params['full_message'])

    def testChunking(self):
        """
        Test the chunking of GELF messages
        """

        longMessage = binascii.hexlify(
            randbytes.insecureRandom(3000)) + 'more!'

        g = GelfProtocol('localhost', **{
            'system': 'protocol',
            'isError': False,
            'message': longMessage,
            'time': time.time(),
        })

        messages = list(g.generate())

        self.failUnless(len(messages) > 1)
        self.failUnless(messages[0].startswith('\x1e\x0f'))

        old_id = None
        for i in xrange(len(messages)):
            magic, chunk_id, seq, num_chunks = struct.unpack(
                '>2s32sHH', messages[i][:38]
            )

            self.assertEquals(magic, '\x1e\x0f')
            self.assertEquals(seq, i)
            self.assertEquals(num_chunks, len(messages))

            if old_id:
                self.assertEquals(chunk_id, old_id)

            old_id = chunk_id
