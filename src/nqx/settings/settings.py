import json
import os
import socket

from pathlib import Path

from ..utils import resolve_env_vars

DATA = None
HOSTNAME = None


def get_root():
    raise NotImplementedError("This function is not implemented yet.")
    root = os.environ.get("NQX_ROOT", None)
    if root is None:
        root = "/Users/filippo.vicentini/Dropbox/Ricerca/Codes/Python/nqx/nqx/src"
        print(f"NQX_ROOT not set. setting it to {root}.")
    return Path(root)


def get_settings():
    global DATA
    if DATA is not None:
        return DATA

    # Load settings from the settings file
    settings_path = resolve_env_vars(get_root() / "etc/config/clusters.json")
    with open(settings_path) as f:
        DATA = json.load(f)

    # Resolve environment variables in the settings
    for key, value in DATA.items():
        if isinstance(value, str):
            DATA[key] = resolve_env_vars(value)
            print("value => ", DATA[key])

    return DATA


def resolve_cluster_name():
    global HOSTNAME
    if HOSTNAME is not None:
        return HOSTNAME

    my_hostname = socket.gethostname()
    settings = get_settings()
    for cluster, cluster_data in settings.items():
        if "hostname" not in cluster_data:
            continue
        if my_hostname.startswith(cluster_data["hostname"]):
            HOSTNAME = cluster
            return HOSTNAME

    return "default"

    # raise FileNotFoundError(f"Could not find cluster for hostname {my_hostname}")


def get_cluster_settings(cluster_name=None):
    if cluster_name is None:
        cluster_name = resolve_cluster_name()

    settings = get_settings()
    return settings.get(cluster_name, {})
