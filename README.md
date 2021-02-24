# MLLP <-> HTTP

[![PyPI](https://img.shields.io/pypi/v/mllp-http)](https://pypi.org/project/mllp-http/)

Convert MLLP to HTTP and vice versa.

Keywords: MLLP, HTTP, HL7, HL7 over HTTP

## Overview

The `http2mllp` program is an HTTP server that converts requests to MLLP.

The `mllp2http` program is an MLLP server that converts messages to HTTP
requests.

Implements
[MLLP release 1](https://www.hl7.org/documentcenter/public/wg/inm/mllp_transport_specification.PDF)
and [HTTP/1.1](https://tools.ietf.org/html/rfc2616). Each MLLP message is
assumed to have a corresponding response content (e.g. HL7 acknoledgment).

Compatible with
[HL7 over HTTP](https://hapifhir.github.io/hapi-hl7v2/hapi-hl7overhttp/specification.html).

Note that this is only MLLP; it does not process HL7v2/HL7v3 messages
themselves. Notably, when used for HL7, the HTTP participant must be able to
read/generate acknowledgements.

## Install

### [Pip](https://pypi.org/project/awscli-saml/)

```sh
pip install mllp-http
```

Run as

```sh
http2mllp mllp://localhost:2575

mllp2http http://localhost:8000
```

### [Docker](https://hub.docker.com/r/rivethealth/aws-saml)

```sh
docker pull rivethealth/mllp-http
```

Run as

```sh
docker run -it -p 2575:2575 rivethealth/mllp-http http2mllp mllp://localhost:2575

docker run -it -p 2575:2575 rivethealth/mllp-http mllp2http http://localhost:8000
```

## Usage

### http2mllp

```
usage: http2mllp [-h] [-H HOST] [-p PORT] [--keep-alive KEEP_ALIVE] [--log-level {error,warn,info}] [--mllp-max-messages MLLP_MAX_MESSAGES] [--mllp-release {1}]
                 [--timeout TIMEOUT] [-v]
                 mllp_url

            HTTP server that proxies an MLLP server.
            Expects an MLLP response message and uses it as the HTTP response.


positional arguments:
  mllp_url              MLLP URL, e.g. mllp://hostname:port

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  HTTP host (default: 0.0.0.0)
  -p PORT, --port PORT  HTTP port (default: 8000)
  --keep-alive KEEP_ALIVE
                        keep-alive in milliseconds, or unlimited if -1. (default: 0)
  --log-level {error,warn,info}
  --mllp-max-messages MLLP_MAX_MESSAGES
                        maximum number of messages per connection, or unlimited if -1. (default: -1)
  --mllp-release {1}    MLLP release version (default: 1)
  --timeout TIMEOUT     socket timeout, in milliseconds, or unlimited if 0. (default: 10000)
  -v, --version         show program's version number and exit
```

### mllp2http

```
usage: mllp2http [-h] [-H HOST] [-p PORT] [--content-type CONTENT_TYPE] [--log-level {error,warn,info}] [--mllp-release {1}]
                 [--timeout TIMEOUT] [-v]
                 http_url

MLLP server that proxies an HTTP server. Sends back the HTTP response.

positional arguments:
  http_url              HTTP URL

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  MLLP host (default: 0.0.0.0)
  -p PORT, --port PORT  MLLP port (default: 2575)
  --content-type CONTENT_TYPE
                        HTTP Content-Type header (default: x-application/hl7-v2+er7)
  --log-level {error,warn,info}
  --mllp-release {1}    MLLP release version (default: 1)
  --timeout TIMEOUT     timeout in milliseconds (default: 10000)
  -v, --version         show program's version number and exit

environment variables:
    HTTP_AUTHORIZATION - HTTP Authorization header
```

## Examples

### mllp2http

Run the HTTP server:

```sh
docker run -p 8000:80 kennethreitz/httpbin
```

Run the MLLP connector:

```sh
mllp2http http://localhost:8000/post
```

Send an MLLP message:

```sh
printf '\x0bMESSAGE\x1c\x0d' | socat - TCP:localhost:2575
```

and see the HTTP server's response, which describes the HTTP request:

```json
{
  "args": {},
  "data": "MESSAGE",
  "files": {},
  "form": {},
  "headers": {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Content-Length": "7",
    "Content-Type": "x-application/hl7-v2+er7",
    "Forwarded": "by=127.0.0.1:2575;for=127.0.0.1:54572;proto=mllp",
    "Host": "localhost:8000",
    "User-Agent": "mllp2http/1.0.2"
  },
  "json": null,
  "origin": "127.0.0.1:54572",
  "url": "mllp://localhost:8000/post"
}
```

## Developing

To install:

```sh
make install
```

Before committing, format:

```sh
make format
```
