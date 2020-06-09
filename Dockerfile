FROM python:3.7-stretch AS build

COPY . /tmp/mllp-http

RUN pip install --no-cache-dir /tmp/mllp-http

FROM gcr.io/distroless/python3-debian10

ENV PYTHONPATH=/usr/local/lib/python3.7/site-packages

RUN python -c "import os; os.makedirs('/usr/local/bin', exist_ok=True); os.symlink('/usr/bin/python', '/usr/local/bin/python')"

COPY --from=build /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages

COPY --from=build /usr/local/bin/http2mllp /usr/local/bin/http2mllp

COPY --from=build /usr/local/bin/mllp2http /usr/local/bin/mllp2http

ENTRYPOINT [ ]