import functools
import socket


def read_socket_bytes(s):
    try:
        for b in iter(functools.partial(s.read, 1), b""):
            yield ord(b)
    except socket.timeout:
        pass
