from typing import Annotated
from enum import Enum
import logging

import typer
import json
import socket
import os

from pathlib import Path

from nqx.utils import resolve_env_vars
from nqx.settings import get_settings, get_root, get_cluster_settings

SEARCH_PATHS = [
    "$NQX_ROOT/config/",
    "/etc/config/nqx/",
    "$NQX_INTERNAL_CONFIG/config/",
]

_config = None


class ConfigDict(dict):
    pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def get_config():
    global _config
    if _config is None:
        _config = _load_config()
    return _config


load_config = get_config


def _load_config():
    config = ConfigDict()

    logging.debug("Loading configuration")
    logging.debug("Searching in %s", SEARCH_PATHS)

    for path in reversed(SEARCH_PATHS):
        path = resolve_env_vars(path)
        logging.debug("Inspecting %s", path)

        # load main config file
        maybe_load_config_file(path / "config.json", config)

        # check cluster specific configurations
        clusters_path = path / "clusters"
        if clusters_path.exists():
            logging.debug("Found clusters path %s", clusters_path)
            hostname = socket.gethostname()
            for cluster in os.listdir(clusters_path):
                cluster_name = os.path.splitext(cluster)[0]
                if hostname.startswith(cluster_name):
                    cluster_path = clusters_path / cluster
                    maybe_load_config_file(cluster_path, config)
                    break
    return config


def maybe_load_config_file(path, config):
    logging.debug("maybe_load_config_file %s", path)
    if not path.exists():
        return
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Invalid configuration file {path} (not valid Json).")
        raise typer.Exit()

    logging.debug("file loaded")
    config.update(data)
    return


def get_requirements_file_for_type(requirement_file_name: Path) -> Path:
    for path in SEARCH_PATHS:
        path = resolve_env_vars(path)
        path = path / requirement_file_name
        if path.exists():
            return path

    raise FileNotFoundError(
        f"Could not find requirements file {requirement_file_name} in {SEARCH_PATHS}"
    )
