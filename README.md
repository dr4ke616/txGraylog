# txGraylog

`txGraylog` is a a twisted based client that interacts with a [Graylog](https://www.graylog.org/) server. Currently it supports the following protocols:
- TCP (Plain text and Gelf protocol)
- UDP (Plain text and Gelf protocol)

There is a plan to implement protocols for HTTP and AMQP.

## Insall from PyPI
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
`txGraylog` can be used by starting a log observer like you would any other python logging module. Alternatively it can also be started as a `Twisted` service.

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

## TODO
- Implement AMQP protocol
- Implement HTTP protocol
- More unit tests
