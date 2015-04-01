# txGraylog

[![Build Status](https://travis-ci.org/dr4ke616/txGraylog.svg)](https://travis-ci.org/dr4ke616/txGraylog)

`txGraylog` is a a twisted based client that interacts with a [Graylog](https://www.graylog.org/) server. Currently it supports the following protocols:
- TCP (Plain text and Gelf protocol)
- UDP (Plain text and Gelf protocol)

There is a plan to implement protocols for HTTP and AMQP.

## Install from PyPI
```
pip install txGraylog
```

## Install from source
```
git clone https://github.com/dr4ke616/txGraylog
pip install -r requirements.txt
python setup.py install
```

## Usage
`txGraylog` can be started by instantiating the log observer class and passing in the protocol, port and address to use. Alternatively it can also be started as a `Twisted` service supplying the same paramaters as the observer. `txGraylog` supports both plain text and [Gelf](https://www.graylog.org/resources/gelf-2/) when using TCP or UDP.

### Observer
When instantiating the observer you need to import the observer class itself and the protocol you wish it use. Below is an example of starting the log observer using UDP.
```python
from txgraylog.protocol import udp
from txgraylog.observer import GraylogObserver

GraylogObserver(udp.UDPGelfProtocol, '127.0.0.1', 6666).start()
```

To instantiate a TCP log observer just import the tcp protocol:
```python
from txgraylog.protocol import tcp
from txgraylog.observer import GraylogObserver

GraylogObserver(tcp.TCPGelfProtocol, '127.0.0.1', 6666).start()
```

To use either UDP or TCP plain text just import `txgraylog.protocol.udp.UDPPlainTextProtocol` or `txgraylog.protocol.tcp.TCPPlainTextProtocol` and pass them as paramaters.

A paramater overide can also be set if you wish to either set additional paramaters or overide the default Python/Graylog paramaters. This can be done by setting the class variable `parameter_override`. This variable exists in all protocols. In the case of it being used in plain text protocols the paramaters will be encoded to string just like the other paramaters passed into the event dictionary.
```python
from txgraylog.protocol import udp
from txgraylog.observer import GraylogObserver

udp.UDPGelfProtocol.parameter_override = {'new_key': 'new_val'}
GraylogObserver(udp.UDPGelfProtocol, '127.0.0.1', 6666).start()
```

### Service
To use `txGraylog` as a Twisted service it is just like starting any other twisted service. Just like the observer you will also need to import the protocol you wish to use:
```python
from txgraylog.protocol import udp
from txgraylog.service import GraylogService

service = GraylogService(udp.UDPGelfProtocol, '127.0.0.1', 6666)
service.setName('Graylog')

application.addService(service)
```

### Log
Logging messages in your application doesnt change. You still import `twisted.python.log` and pass in the messages or errors you want by calling `msg` or `err`. However `txGraylog` adds additional functionality where you can pass in extra key value arguments that can be understood by the Graylog server. For example:
```python
from twisted.python import log

log.msg('Some log message', customer_id=1234, app='my_application')
```
Its important to note that if you have a standard file log observer setup the key value arguments that you pass wont appear in the log files. These are only understood by the `txGraylog` client.

## TODO
- Implement AMQP protocol
- Implement HTTP protocol
- More unit tests

## Known Issues
- When instantiating more than one log observer that uses two different protocols for the same host, for example a TCP and a UDP observer, if the TCP connection should drop `twisted` will stop the TCP factory. But for some reason `Twisted` will also stop the UDP factory. This means the UDP connection will fail to reconnect unless you restart your application. This wont be a problem for TCP as it implements the `ReconnectingClientFactory`.
