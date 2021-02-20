import functools
import logging
import os
import requests
import socketserver
import urllib
from .mllp import read_mllp, write_mllp
from .version import __version__

logger = logging.getLogger(__name__)


def display_address(address):
    return f"{address[0]}:{address[1]}"


class MllpServerOptions:
    def __init__(self, timeout):
        self.timeout = timeout


class MllpHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, address, server, timeout, http_url, http_options):
        self.http_url = http_url
        self.http_options = http_options
        self.timeout = timeout
        super().__init__(request, address, server)

    def handle(self):
        self.request.settimeout(self.timeout)
        session = requests.Session()
        local_address = self.request.getsockname()
        remote_address = self.request.getpeername()

        try:
            for message in read_mllp(self.rfile):
                try:
                    logger.info("Message: %s bytes", len(message))
                    headers = {
                        "Forwarded": f"by={display_address(local_address)};for={display_address(remote_address)};proto=mllp",
                        "User-Agent": f"mllp2http/{__version__}",
                        "X-Forwarded-For": display_address(remote_address),
                        "X-Forwarded-Proto": "mllp",
                    }
                    try:
                        headers["Authorization"] = os.environ["HTTP_AUTHORIZATION"]
                    except KeyError:
                        pass
                    if self.http_options.content_type is not None:
                        headers["Content-Type"] = self.http_options.content_type
                    response = session.post(
                        urllib.parse.urlunparse(self.http_url),
                        data=message,
                        headers=headers,
                        timeout=self.http_options.timeout,
                    )
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    logger.error("HTTP response error: %s", e.response.status_code)
                    break
                except Exception as e:
                    logger.error("HTTP connection error: %s", e)
                    break
                else:
                    content = response.content
                    logger.info("Response: %s bytes", len(content))
                    write_mllp(self.wfile, content)
                    self.wfile.flush()
        except Exception as e:
            logger.error("Failed read MLLP message: %s", e)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class HttpClientOptions:
    def __init__(self, content_type, timeout):
        self.content_type = content_type
        self.timeout = timeout


def serve(address, options, http_url, http_options):
    logger = logging.getLogger(__name__)

    handler = functools.partial(
        MllpHandler,
        http_url=http_url,
        http_options=http_options,
        timeout=options.timeout,
    )

    server = ThreadedTCPServer(address, handler)
    logger.info("Listening on %s:%s", address[0], address[1])
    server.serve_forever()
