import functools
import http.server
import logging
import socket
import threading
import time
from .mllp import read_mllp,write_mllp_socket
from .net import read_real_socket_bytes

logger = logging.getLogger(__name__)


class MllpClientOptions:
    def __init__(self, keep_alive, max_messages, timeout):
        self.keep_alive = keep_alive
        self.max_messages = max_messages
        self.timeout = timeout


class MllpClient:
    def __init__(self, address, options):
        self.address = address
        self.options = options
        self.connections = []
        self.lock = threading.Lock()

    def _check_connection(self,connection):
        while not connection.closed:
            elapsed = (
                connection.last_update - time.monotonic()
                if connection.last_update is not None
                else 0
            )
            remaining = self.options.keep_alive + elapsed
            if 0 < remaining:
                time.sleep(remaining)
            else:
                try:
                    with self.lock:
                        self.connections.remove(connection)
                except ValueError:
                    pass
                else:
                    connection.close()

    def _connect(self):
        logger.info("connecting to "+self.address[0]+":"+self.address[1])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.options.timeout:
            s.settimeout(self.options.timeout)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 10)
        s.connect(self.address)
        connection = MllpConnection(s)
        if self.options.keep_alive is not None:
            thread = threading.Thread(
                daemon=False, target=self._check_connection, args=(connection,)
            )
            thread.start()
        return connection

    def send(self, data):
        with self.lock:
            try:
                connection = self.connections.pop()
            except IndexError:
                connection = None
            else:
                connection.last_update = None
        if connection is None:
            connection = self._connect()
        response = connection.send(data)
        if self.options.max_messages > 0 and self.options.max_messages <= connection.message_count:
            connection.close()
        else:
            connection.last_update = time.monotonic()
            with self.lock:
                self.connections.append(connection)
        return response

class MllpConnection:
    def __init__(self, socket):
        self.cancel = None
        self.closed = False
        self.socket = socket
        self.responses = read_mllp(read_real_socket_bytes(self.socket))
        self.message_count=0
        self.last_update = time.monotonic()

    def close(self):
        self.closed = True
        self.socket.close()

    def send(self,data):
        write_mllp_socket(self.socket, data)
        # self.socket.flush()
        self.message_count += 1
        return next(self.responses)
    
class HttpServerOptions:
    def __init__(self, timeout):
        self.timeout = timeout


class HttpHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server,mllp_client):
        self.mllp_client = mllp_client
        super().__init__(request,client_address,server)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        data = self.rfile.read(content_length)
        logger.info("Message: %s bytes", len(data))
        response = self.mllp_client.send(data)
        logger.info("Response: %s bytes", len(response))
        self.send_response(201)
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)


def serve(address, options, mllp_address, mllp_options):
    client = MllpClient(mllp_address, mllp_options)
    handler = functools.partial(
        HttpHandler,
        mllp_client=client,
    )

    server = http.server.ThreadingHTTPServer(address,handler)
    server.protocol_version = "HTTP/1.1"
    logger.info("HTTP server on %s:%s", address[0], address[1])
    server.serve_forever()
