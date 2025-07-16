""" 
Module: logs
"""


# Pylint rules
# pylint: disable=superfluous-parens
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=broad-exception-caught
# pylint: disable=import-error

import logging
import json
from datetime import datetime
from websockets.sync.client import connect

def init_logger():
    """
    Defines and initialize logger
    """

    log_format = '%(message)s'

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def log_message(message):
    """ Write log message
    """

    current_datetime = datetime.now()
    print( f"{current_datetime.isoformat()}Z - {message}", flush=True)


def log_to_websocket_server(ip_addr:str, port:int=29784, message:str='payload')->None:
    """
    Log a message to a WebSocket server
    """
    # uri to reach the ws server
    uri = f"ws://{ip_addr}:{port}"
    try:
        dict_message = { 'method': 'snapshot', 'data': message };
        # conect to the ws server
        with connect(uri) as websocket:
            # write message
            websocket.send(json.dumps(dict_message))
    except Exception as e:
        # nothing to do
        log_message( e )
        # pass
