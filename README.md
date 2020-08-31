# AWS SAML CLI

[![PyPi](https://img.shields.io/pypi/v/mllp-http)](https://pypi.org/project/awscli-saml/)

Convert MLLP to HTTP and vice versa.

## Overview

The `http2mllp` program is an HTTP server that converts requests to MLLP.

The `mllp2http` program is an MLLP server that converts messages to HTTP requests.

Implements [MLLP release 1](https://www.hl7.org/documentcenter/public/wg/inm/mllp_transport_specification.PDF) and [HTTP/1.1](https://tools.ietf.org/html/rfc2616).
Each MLLP message is assumed to have a corresponding response contnet.

Roughly compatible with [HL7 over HTTP](https://hapifhir.github.io/hapi-hl7v2/hapi-hl7overhttp/specification.html).

Note that this is only MLLP; it does not process HL7v2/HL7v3 messages. Notably, when used for HL7, the HTTP side must be able to read/generate acknowledgements.

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
docker run -it -p 2575:2575 rivethealth/mllp-http http2mllp http://localhost:8000

docker run -it -p 2575:2575 rivethealth/mllp-http mllp2http http://localhost:8000
```

## Usage

```
usage: http2mllp [-h] [-H HOST] [-p PORT] [--keep-alive KEEP_ALIVE]
                 [--log-level {error,warn,info}]
                 [--mllp-max-messages MLLP_MAX_MESSAGES] [--mllp-release {1}]
                 [--timeout TIMEOUT] [-v]
                 mllp_url

HTTP server that proxies an MLLP server. Expects an MLLP response message and
uses it as the HTTP response.

positional arguments:
  mllp_url              MLLP URL, e.g. mllp://hostname:port

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  HTTP host
  -p PORT, --port PORT  HTTP port
  --keep-alive KEEP_ALIVE
                        Keep-alive in milliseconds, or unlimited if -1.
  --log-level {error,warn,info}
  --mllp-max-messages MLLP_MAX_MESSAGES
                        Maximum number of messages per connection, or
                        unlimited if -1.
  --mllp-release {1}    MLLP release version
  --timeout TIMEOUT     Socket timeout, in milliseconds, or unlimited if 0.
  -v, --version         show program's version number and exit
```

```
usage: mllp2http [-h] [-H HOST] [-p PORT] [--content-type CONTENT_TYPE]
                 [--log-level {error,warn,info}] [--mllp-release {1}]
                 [--timeout TIMEOUT] [-v]
                 http_url

MLLP server that proxies an HTTP server. Sends back the HTTP response.

positional arguments:
  http_url              HTTP URL

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  MLLP host
  -p PORT, --port PORT  MLLP port
  --content-type CONTENT_TYPE
                        HTTP Content-Type header
  --log-level {error,warn,info}
  --mllp-release {1}    MLLP release version
  --timeout TIMEOUT     timeout in milliseconds
  -v, --version         show program's version number and exit

environment variables:
    HTTP_AUTHORIZATION - HTTP Authorization header
```
