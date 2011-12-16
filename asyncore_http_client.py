import asyncore, socket, sys

class HTTPClient(asyncore.dispatcher):

    def __init__(self, host, path):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, 80) )
        self.buffer = 'GET %s HTTP/1.0\r\n\r\n' % path

    def handle_connect(self):
        print 'connected'
        pass

    def handle_close(self):
        print 'closing'
        self.close()

    def handle_read(self):
        print 'receiving'
        data = self.recv(8192)
        print data

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        print 'sending'
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]
if __name__ == '__main__':
    client = HTTPClient(*sys.argv[1:])
    asyncore.loop()



## FROM EFFBOT

import asyncore
import socket, time
import StringIO
import mimetools, urlparse

class async_http(asyncore.dispatcher_with_send):
    # asynchronous http client

    def __init__(self, host, port, path, consumer):
        asyncore.dispatcher_with_send.__init__(self)

        self.host = host
        self.port = port
        self.path = path

        self.consumer = consumer

        self.status = None
        self.header = None

        self.bytes_in = 0
        self.bytes_out = 0

        self.data = ""

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_connect(self):
        # connection succeeded
        text = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (self.path, self.host)
        self.send(text)
        self.bytes_out = self.bytes_out + len(text)

    def handle_expt(self):
        # connection failed; notify consumer
        self.close()
        self.consumer.http_failed(self)

    def handle_read(self):

        data = self.recv(2048)
        self.bytes_in = self.bytes_in + len(data)

        if not self.header:
            # check if we've seen a full header

            self.data = self.data + data

            header = self.data.split("\r\n\r\n", 1)
            if len(header) <= 1:
                return
            header, data = header

            # parse header
            fp = StringIO.StringIO(header)
            self.status = fp.readline().split(" ", 2)
            self.header = mimetools.Message(fp)

            self.data = ""

            self.consumer.http_header(self)

            if not self.connected:
                return # channel was closed by consumer

        if data:
            self.consumer.feed(data)

    def handle_close(self):
        self.consumer.close()
        self.close()

def do_request(uri, consumer):

    print 'making http request: %s' % uri

    # turn the uri into a valid request
    scheme, host, path, params, query, fragment = urlparse.urlparse(uri)
    assert scheme == "http", "only supports HTTP requests"
    try:
        host, port = host.split(":", 1)
        port = int(port)
    except (TypeError, ValueError):
        port = 80 # default port
    if not path:
        path = "/"
    if params:
        path = path + ";" + params
    if query:
        path = path + "?" + query

    return async_http(host, port, path, consumer)

class CallbackConsumer(object):
    def __init__(self,callback):
        self.callback = callback
        self.host = None
        self.data = ''

    def http_header(self, client):
        self.host = client.host

    def http_failed(self, client):
        self.callback(None)

    def feed(self, data):
        self.data += data

    def close(self):
        print 'callback consumer close'
        self.callback(self.data)

def async_request(url,callback):
    return do_request(url, CallbackConsumer(callback))
