import http.server
import logging
import threading
import time
from .mllp import write_mllp

logger = logging.getLogger(__name__)


class MllpClientOptions:
    def __init__(self, keep_alive, max_messages, timeout):
        self.address = address
        self.keep_alive = keep_alive
        self.max_messages = max_messages
        self.timeout = timeout


class MllpClient:
    def __init__(self, address, options):
        self.address = address
        self.options = self.options
        self.connections = []
        self.lock = threading.Lock()

    def _check_connection(connection):
        while not connection.closed:
            elasped = (
                connection.last_update - time.monotonic()
                if connection.last_update is not None
                else 0
            )
            remaining = self.keep_alive + elasped
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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.options.timeout)
        s.connect(self.address)
        connection = MllpConnection(s)
        if self.keep_alive is not None:
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
        if self.options.max_messages <= connection.message_count:
            connection.close()
        else:
            connection.last_update = time.monotonic()
            with self.lock:
                self.connections.append(connection)
        return response


class MllpConnection:
    def __init__(self, socket):
        self.closed = False
        self.last_update = None
        self.message_count = 0
        self.socket = socket

    def close():
        self.close = True
        self.socket.shutdown()
        self.socket.close()


class MllpConnection:
    def __init__(self, socket):
        self.address = address
        self.cancel = None
        self.closed = False
        self.responses = read_mllp(self.socket)
        self.socket = socket

    def close():
        self.closed = True
        self.socket.close()

    def send(data):
        write_mllp(self.socket, data)
        self.socket.flush()
        self.message_count += 1
        return next(self.responses)


class HttpServerOptions:
    def __init__(self, timeout):
        self.timeout = timeout


class HttpHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, mllp_client, content_type, timeout, keep_alive):
        self.content_type = content_type
        self.mllp_client = mllp_client
        self.timeout = timeout

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        data = self.rfile.read(content_length)
        logger.info("Message: %s bytes", len(data))
        response = self.mllp_client.send(data)
        logger.info("Response: %s bytes", len(response))
        self.send_response(201)
        self.send_header("Content-Length", len(response))
        if self.content_type:
            self.send_header("Content-Type", self.content_type)
        if self.keep_alive is not None:
            self.send_header("Keep-Alive", f"timeout={self.keep_alive}")
        self.end_headers()
        self.wfile.write(response)


def serve(address, options, mllp_address, mllp_options):
    client = MllpClient(mllp_address, mllp_options)

    handler = functools.partial(
        HttpHandler,
        content_type=options.content_type,
        keep_alive=options.keep_alive,
        mllp_client=client,
        timeout=options.timeout,
    )

    server = http.server.ThreadingHTTPServer(address)
    server.protocol_version = "HTTP/1.1"
    server.serve_forever()
