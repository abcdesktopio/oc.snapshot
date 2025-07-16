""" Main module
"""

# Pylint rules
# pylint: disable=superfluous-parens
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=broad-exception-caught
# pylint: disable=import-error

import json
from time import time_ns
from datetime import datetime
from threading import Thread
import yaml
from flask import Flask, jsonify
from flask_cors import CORS
from cachetools import TTLCache

from helpers.logs import log_message,init_logger,log_to_websocket_server
from helpers.version import API_VERSION
from helpers.nerdctl import registry_login
from helpers.nerdctl import registry_push
from helpers.nerdctl import get_container_id
from helpers.nerdctl import registry_image_commit
from helpers.nerdctl import get_image_name
from helpers.nerdctl import NerdctlException
from helpers.settings import ABCDESKTOP_USERID
from helpers.settings import POD_IP

app = Flask(__name__)
CORS(app, origins=["*"])

console_logger = init_logger()


# Cache for session data, TTL of 20 minutes.
# maxsize: 1 million entries, ttl: 1200 seconds (20 minutes).
session_cache = TTLCache(maxsize=10**6, ttl=20*60)


def broadcast_message( message:str ):
    """
    Broadcast message to the websocket server.
    """
    if isinstance( POD_IP, str ):
        log_to_websocket_server( ip_addr=POD_IP, message=message )

def process_snapshot(p_session_id: str) -> None:
    """
    Snapshot of the current state of the system.
    """
    image_name = get_image_name()

    try:
        session_cache[p_session_id]['status'] = "search desktop id"
        container_id=get_container_id(p_session_id)
        if container_id == "unknown":
            log_message("container not found for session - " + p_session_id)

        session_cache[p_session_id]['status'] = "generate desktop image"
        broadcast_message( 'generating desktop image' )
        registry_image_commit(p_session_id,container_id,image_name)
        broadcast_message( 'desktop image is generated' )

        session_cache[p_session_id]['status'] = "login to registry"
        registry_login(p_session_id)

        session_cache[p_session_id]['status'] = "push desktop image to registry"
        broadcast_message( "pushing desktop image to registry" )
        registry_push(p_session_id,image_name)
        broadcast_message( "desktop image is pushed"  )

        session_cache[p_session_id]['status'] = "done"
    except NerdctlException:
        session_cache[p_session_id]['status'] = "error"

def json_response_maker(current_message,current_status,p_session_id=None):
    """
    Generate a json structured answer from parameters
    and return it
    """
    response = {
        'message': current_message,
        'status': current_status,
        'timestamp': datetime.now(),
        'session_id': p_session_id if p_session_id else 'none',
        'api_version': API_VERSION
    }

    return jsonify(response)

@app.route('/version', methods=['GET'], strict_slashes=False)
def version():
    """
    Return the current api version
    """
    log_message("Call /version")
    return json_response_maker('version is ' + API_VERSION,"success"),200


@app.route('/snapshot/<string:p_session_id>', methods=['GET'], strict_slashes=False)
def snapshot_status(p_session_id):
    """
    Get snapshot status of the session id.
    """

    if p_session_id not in session_cache:
        return json_response_maker('unknown session',"error",p_session_id),404

    return json_response_maker(session_cache[p_session_id]['status'],"success",p_session_id),200


@app.route('/snapshots/', methods=['GET'], strict_slashes=False)
def snapshots_status():
    """
    Get snapshots status of the user_id.
    """

    result = []
    for session_id, data in session_cache.items():
        if data.get('user_id') == ABCDESKTOP_USERID:
            result.append({
                'session_id': session_id,
                'status': data.get('status'),
            })
    if len(result) == 0:
        return json_response_maker('no snapshot operations',"error"),404
    return json_response_maker(json.dumps(result),"success"),200


#    return json_response_maker(session_cache.get[session_id]['status'],"success",p_session_id),200

@app.route('/snapshot', methods=['POST'], strict_slashes=False)
def snapshot():
    """
    Snapshot of the current state of the system.
    """
    session_id = str(time_ns())

    session_cache[session_id] = {
        "status": "starting",
        "user_id": ABCDESKTOP_USERID
    }

    thread = Thread(target=process_snapshot, args=(session_id,))
    thread.start()
    return json_response_maker('snapshot process started',"success",session_id),200

@app.route('/swagger.json',methods=['GET'])
@app.route('/swagger', methods=['GET'], strict_slashes=False)
def swagger():
    """
    Return the swagger description of the api
    """
    try:
        with open('swagger/swagger.yaml', 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        return jsonify(spec)
    except FileNotFoundError:
        log_message("Error opening swagger.yaml")
        return json_response_maker("Error opening swagger.yaml","error"),500
    except yaml.YAMLError as e:
        log_message("Invalid swagger YAML syntax:"+ str(e))
        return json_response_maker("Invalid swagger YAML syntax","error"),500

@app.errorhandler(404)
def page_not_found(error):
    """
    Return the default error message if no
    API corresponds to the call.
    """
    return json_response_maker('unsupported page','error'),404
