import functools
import logging


class Format:
    START_BLOCK = 0x0B
    END_BLOCK = 0x1C
    CARRAIGE_RETURN = 0x0D


class State:
    AFTER_BLOCK = 0
    BEFORE_BLOCK = 1
    BLOCK = 2


def read_bytes(file):
    for b in iter(functools.partial(file.read1, 1), b""):
        yield ord(b)


def to_hex(byte):
    return "EOF" if byte is None else hex(byte)


def read_mllp(rfile):
    logger = logging.getLogger("mllp.parse")

    content = None
    state = State.BEFORE_BLOCK
    byte = None
    it = read_bytes(rfile)
    byte = None
    i = -1

    def advance():
        nonlocal byte
        nonlocal i
        byte = next(it, None)
        i += 1

    advance()
    while True:
        if state == State.AFTER_BLOCK:
            if byte == Format.CARRAIGE_RETURN:
                state = State.BEFORE_BLOCK
                advance()
            else:
                logger.error(
                    "Expected %s instead of %s (byte:%s)",
                    to_hex(Format.CARRAIGE_RETURN),
                    to_hex(byte),
                    i,
                )
                break
        elif state == State.BEFORE_BLOCK:
            if byte is None:
                break
            if byte == Format.START_BLOCK:
                content = bytearray()
                state = State.BLOCK
                advance()
            else:
                logger.error(
                    "Expected %s instead of %s (byte:%s)",
                    to_hex(Format.START_BLOCK),
                    to_hex(byte),
                    i,
                )
                break
        elif state == State.BLOCK:
            if byte == Format.START_BLOCK:
                logger.error(
                    "Expected content instead of %s (byte:%s)",
                    to_hex(Format.CARRAIGE_RETURN),
                    to_hex(byte),
                    i,
                )
                break
            elif byte == Format.END_BLOCK:
                yield bytes(content)
                content = None
                state = State.AFTER_BLOCK
                advance()
            else:
                content.append(byte)
                advance()


def write_mllp(wfile, content):
    wfile.write(bytes([Format.START_BLOCK]))
    wfile.write(content)
    wfile.write(bytes([Format.END_BLOCK, Format.CARRAIGE_RETURN]))
