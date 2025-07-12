""" Main module
"""

# Pylint rules
# pylint: disable=superfluous-parens
# pylint: disable=invalid-name
# pylint: disable=unused-argument
# pylint: disable=broad-exception-caught
# pylint: disable=import-error

#import json

from time import time_ns
from datetime import datetime
# import requests
import yaml

from flask import Flask, jsonify
from flask_cors import CORS

from helpers.logs import log_message,init_logger
from helpers.version import API_VERSION
from helpers.nerdctl import registry_login
from helpers.nerdctl import registry_push
from helpers.nerdctl import get_container_id
from helpers.nerdctl import registry_image_commit
from helpers.nerdctl import get_image_name
from helpers.nerdctl import NerdctlException

app = Flask(__name__)
CORS(app, origins=["*"])

console_logger = init_logger()


def json_response_maker(current_message,current_status):
    """
    Generate a json structured answer from parameters
    and return it
    """
    response = {
        'message': current_message,
        'status': current_status,
        'timestamp': datetime.now()
    }

    return jsonify(response)

@app.route('/version', methods=['GET'], strict_slashes=False)
def version():
    """
    Return the current api version
    """
    log_message("Call /version")
    return json_response_maker('version is ' + API_VERSION,"success"),200


@app.route('/snapshot', methods=['POST'], strict_slashes=False)
def snapshot():
    """
    Snapshot of the current state of the system.
    """

    session_id = str(time_ns())
    image_name = get_image_name()

    log_message("Starting session - " + session_id+" -- " +
                 "image_name "+image_name)
    try:
        container_id=get_container_id(session_id)
        if container_id == "unknown":
            log_message("Container not found for session - " + session_id)
        registry_image_commit(session_id,container_id,image_name)

        registry_login(session_id)
        registry_push(session_id,image_name)

        return json_response_maker('image pushed to registry',"success"),200
    except NerdctlException as e:
        return json_response_maker("error"+e.args[0],"error"),200

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
