import functools
import socket


def read_socket_bytes(socket):
    try:
        for b in iter(functools.partial(socket.read, 1), b""):
            yield ord(b)
    except socket.timeout:
        pass
