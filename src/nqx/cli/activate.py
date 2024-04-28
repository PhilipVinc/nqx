from typing import Annotated
from enum import Enum
from pathlib import Path
import shutil
import os
import logging

from rich import print
import typer

from nqx.core import EnvConfig, EnvType, VenvProviderType, PythonProviderType
from nqx.providers import get_venv_provider, get_python_provider, modules

from .config import get_config, get_requirements_file_for_type
from .app import app


@app.command(no_args_is_help=True)
def activate(
    name: Annotated[str, typer.Argument(help="The name of the environment.")],
):
    """
    Create a new environment with NAME of type TYPE
    """
    config = get_config()

    # Create EnvConfig
    env_config = EnvConfig(env={})

    ###############################################################
    # Get Python : not needed for activating the environment as
    # it is set by the virtualenv activation script
    python_provider = get_python_provider()
    env_config = python_provider.get_env_with_python(env_config)

    ###############################################################
    # Create the virtual environment
    provider = get_venv_provider(VenvProviderType(config["venv_provider"]))
    venv_depot = config["venv_location"]
    env_config = provider.activate_env(name, venv_depot=venv_depot, environment=env_config)

    ###############################################################
    # Setup env variables
    type = provider.get_env_type(name, venv_depot)
    env_config.update(config["configurations"][type.value].get("env", {}))

    ###############################################################
    # Setup modules
    modules_to_load = config["configurations"][type.value].get("modules", [])
    if len(modules_to_load) > 0:
        logging.debug("Loading modules")
        env_config = modules.load_modules(*modules_to_load, environment=env_config)

    ###############################################################
    # 
    for k, v in env_config.env.items():
        print(f"export {k}={v}")