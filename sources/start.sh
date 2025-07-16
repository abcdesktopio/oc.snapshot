#!/bin/sh
LISTEN_IP=${POD_IP:-'0.0.0.0'}
flask --app main run --host=$LISTEN_IP --port=29785
