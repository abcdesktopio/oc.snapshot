""" Module nerdctl """

import subprocess
from typing import Final
from time import time_ns

from helpers.logs import log_message
from helpers.settings import ABCDESKTOP_USERID
from helpers.settings import SNAPSHOT_REGISTRY_USERNAME
from helpers.settings import SNAPSHOT_REGISTRY_PASSWORD
from helpers.settings import SNAPSHOT_REGISTRY_REGISTRY
from helpers.settings import SNAPSHOT_CONTAINER_TARGET_IMAGE
from helpers.settings import SNAPSHOT_CONTAINER_NAME
from helpers.settings import DEBUG_LEVEL

DEFAULT_NAMESPACE:Final[str]  = 'k8s.io'

class NerdctlException(Exception):
    """
    This class represents an exception that can be raised when there is a problem
    with Nerdctl.
    """

def get_image_name():
    """
    This function constructs and returns the image name by concatenating the base target
    image name, a unique username, and a timestamp in nanoseconds. The constructed string
    is used as a unique identifier for the Docker images created in the system.

    Returns:
        str: A formatted string that represents a uniquely identified Docker image name
        based on SNAPSHOT_CONTAINER_TARGET_IMAGE, ABCDESKTOP_USERID and current
        timestamp in nanoseconds. The format is: "<target_image>-<current_timestamp>".
    """
    return SNAPSHOT_CONTAINER_TARGET_IMAGE + "-" + str(time_ns())

def registry_login(p_session_id):
    """
    This function attempts to log into a Docker registry using the provided session ID. It uses
    subprocess module to execute 'nerdctl login' command with credentials stored in constants
    SNAPSHOT_REGISTRY_USERNAME and SNAPSHOT_REGISTRY_PASSWORD. If successful, it returns True;
    otherwise, it raises a NerdctlException. The output or errors from the subprocess are also
    logged for debugging purposes.

    Args:
        p_session_id (str): A unique session identifier used in logging messages to track
        specific actions throughout their lifecycle.

    Returns:
        bool: True if login is successful, otherwise raises a NerdctlException.

    Raises:
        NerdctlException: If the 'nerdctl login' command fails for any reason.
    """

    log_message("Login to registry - "+p_session_id)

    cmd = [ "nerdctl",
            "login",
            SNAPSHOT_REGISTRY_REGISTRY,
            "--username",
            SNAPSHOT_REGISTRY_USERNAME,
            "--password",
            SNAPSHOT_REGISTRY_PASSWORD ]

    result = subprocess.run(cmd, capture_output=True, text=True,check=True)

    # Check if the login was successful
    if result.returncode != 0:
        log_message("Login to rgistry failed - "+p_session_id)
        log_message("Sortie standard:"+ result.stdout)
        log_message("Erreur standard:"+ result.stderr)
        raise NerdctlException("Login to registry failed")

    # Log that the login was successful
    log_message("Login to registry successful - "+p_session_id)
    return True

def get_container_id(p_session_id):
    """
    This function retrieves the ID of a running Docker container using 'nerdctl ps' command. It
    searches for containers that have SNAPSHOT_CONTAINER_NAME in their names and returns the
    first match. If no matching container is found, it raises a NerdctlException. The output or
    errors from the subprocess are also logged for debugging purposes.

    Args:
        p_session_id (str): A unique session identifier used in logging messages to track specific
        actions throughout their lifecycle.

    Returns:
        str: ID of the first matching Docker container if found, otherwise raises a
        NerdctlException.

     Raises:
        NerdctlException: If no containers with SNAPSHOT_CONTAINER_NAME are found or if the
        'nerdctl ps' command fails for any reason.
       """
    log_message("Search container id - "+p_session_id)

    container_id = "unknown"

    cmd = ["nerdctl",
           "-n",
           DEFAULT_NAMESPACE,
           "ps"]

    result = subprocess.run(cmd, capture_output=True, text=True,check=True)
    if result.returncode != 0:
        log_message("Get container id failed - "+p_session_id)
        log_message("Sortie standard:"+ result.stdout)
        log_message("Erreur standard:"+ result.stderr)
        raise NerdctlException("Search container id failed")

    lines = result.stdout.strip().split('\n')
    container_lines = lines[1:]

    for line in container_lines:
        parts = [part for part in line.split("  ") if part.strip()]
        parts = [p.strip() for p in parts]
        if len(parts) >= 6:

            if SNAPSHOT_CONTAINER_NAME in parts[5]:
                container_id = parts[0]
                if DEBUG_LEVEL == "DEBUG":
                    log_message("--- container_id:"+ parts[0])
                    log_message("--- image:"+ parts[1])
                    log_message("--- command:"+ parts[2])
                    log_message("--- created:"+ parts[3])
                    log_message("--- status:"+ parts[4])
                    log_message("--- ports:"+ parts[5] )

    log_message("Search container id successful - "+p_session_id+"-->"+container_id)
    return container_id

def registry_image_commit(p_session_id,p_container_id,p_image_name):
    """
    This function creates a Docker image for the registry from a specified container. It uses
    'nerdctl commit' command to create an image with the provided container ID and image name.
    If successful, it returns True; otherwise, it raises a NerdctlException. The output or errors
    from the subprocess are also logged for debugging purposes.

    Args:
        p_session_id (str): A unique session identifier used in logging messages to track specific
        actions throughout their lifecycle.

        p_container_id (str): ID of the Docker container that needs to be committed into an image.

        p_image_name (str): Name for the new Docker image created from the container.

       Returns:
           bool: True if commit is successful, otherwise raises a NerdctlException.

       Raises:
           NerdctlException: If the 'nerdctl commit' command fails for any reason.
       """

    log_message("Commit image for registry - "+p_session_id)
    cmd = [ "nerdctl",
            "-n",
            DEFAULT_NAMESPACE,
            "commit",
            p_container_id,
            p_image_name ]

    result = subprocess.run(cmd, capture_output=True, text=True,check=True)
    if result.returncode != 0:
        log_message("Commit image for registry failed - "+p_session_id)
        log_message("Sortie standard:"+ result.stdout)
        log_message("Erreur standard:"+ result.stderr)
        raise NerdctlException("Commit imaage for registry failed")

    log_message("Commit image for registry successful - "+p_session_id)
    return True

def registry_push(p_session_id,p_image_name):
    """
    This function pushes the specified Docker image to a remote registry using 'nerdctl push'
    command. It takes in the session ID and image name as arguments. If the push is successful,
    it returns True; otherwise, it raises a NerdctlException. The output or errors from the
    subprocess are also logged for debugging purposes.

    Args:
        p_session_id (str): A unique session identifier used in logging messages to track specific
        actions throughout their lifecycle.

        p_image_name (str): Name of the Docker image that needs to be pushed to the registry.

    Returns:
        bool: True if push is successful, otherwise raises a NerdctlException.

    Raises:
        NerdctlException: If the 'nerdctl push' command fails for any reason.
    """

    log_message("Push image to registry - "+p_session_id)

    cmd = ["nerdctl",
           "-n",
           DEFAULT_NAMESPACE,
           "push",
           p_image_name]

    result = subprocess.run(cmd, capture_output=True, text=True,check=True)
    if result.returncode != 0:
        log_message("Commit image for registry failed - "+p_session_id)
        log_message("Sortie standard:"+ result.stdout)
        log_message("Erreur standard:"+ result.stderr)
        raise NerdctlException("Push image to registry failed")

    log_message("Push image to registry successful - "+p_session_id)
    return True
