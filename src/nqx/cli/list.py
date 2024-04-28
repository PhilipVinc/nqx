from typing import Annotated
from enum import Enum
from pathlib import Path

from rich import print
import typer

from nqx.core import EnvType, ProviderType
from nqx.providers import get_venv_provider

from .config import get_config
from .app import app


@app.command()
def list():
    """
    List all environments
    """
    config = get_config()
    venv_depot = config["venv_location"]

    provider = config["venv_provider"]

    venv_depot = config["venv_location"]
    provider = get_venv_provider(provider)

    envs = provider.list_envs(venv_depot)

    print()
    print("# Available NQX-friendly environments are:")
    print(f"# {'name':<20} \t {'type':<5} \t {'path'}")
    for name, path in envs:
        type = provider.get_env_type(name, venv_depot).value
        if type is None:
            type = "?"

        print(f"- {name:<20} \t {type:<5} \t {path}")

    return 0


@app.command()
def config():
    """
    List all environments
    """

    config = get_config()

    print()
    print("# NQX Configuration")
    for k, v in config.items():
        print(f" {k:<20} \t {v}")
