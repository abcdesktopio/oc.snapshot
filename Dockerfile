FROM python:3.14-rc-alpine

WORKDIR /app
COPY sources /app


run apk update && \
    apk upgrade  && \
    apk add --no-cache nerdctl && \
    pip install --upgrade pip && \
    pip install -qU flask-cors && \
    pip install -qU flask && \
    pip install -qU cachetools && \
    pip install -qU PyYAML && \
    pip install -qU websockets && \
    echo "API_VERSION=$(date +\"%Y%m%d.%H.%M.%S\")" > /app/helpers/version.py

EXPOSE 29785

CMD  ["/app/start.sh"]
