# MLLP/HTTP

[![PyPI](https://img.shields.io/pypi/v/mllp-http)](https://pypi.org/project/mllp-http/)

<p align="center">
  <img src="doc/logo.png">
</p>

## Overview

Convert MLLP to HTTP and vice versa.

`http2mllp` is an HTTP server that converts HTTP requests to MLLP messages and
MLLP messages to HTTP responses.

`mllp2http` is an MLLP server that converts MLLP messages to HTTP requests and HTTP
responses to MLLP messages.

Keywords: MLLP, HTTP, HL7, HL7 over HTTP

## Description

MLLP (Minimum Lower Layer Protocol) is the traditional session protocol for HL7
messages.

Many modern tools (load balancers, application frameworks, API monitoring) are
designed around HTTP. This observation is the foundation for the
[HL7 over HTTP](https://hapifhir.github.io/hapi-hl7v2/hapi-hl7overhttp/specification.html)
specification.

This project, MLLP/HTTP, bridges these two protocols, allowing network engineers
and application developers to work with familiar HTTP technlogy while
interfacing with MLLP-based programs.

Implements
[MLLP release 1](https://www.hl7.org/documentcenter/public/wg/inm/mllp_transport_specification.PDF)
and [HTTP/1.1](https://tools.ietf.org/html/rfc2616). Each MLLP message is
assumed to have a corresponding response content (e.g. HL7 acknoledgment).

Note that this project deals only with the MLLP layer; it does not process HL7
messages themselves. Notably, the HTTP participant must be able to intepret HL7
messages and generate acknowledgements. This separation imposes no requirements
for HL7 usage and leaves application developers with full access to the features
of the HL7 protocol.

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
  --timeout TIMEOUT     socket timeout, in milliseconds, or unlimited if 0. (default: 0)
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
  --timeout TIMEOUT     timeout in milliseconds (default: 0)
  -v, --version         show program's version number and exit

environment variables:
    HTTP_AUTHORIZATION - HTTP Authorization header
    API_KEY - HTTP X-API-KEY header
```

## Examples

### mllp2http

Run an HTTP debugging server:

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

and see the HTTP server's response (which describes the HTTP request that the
connector made):

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
