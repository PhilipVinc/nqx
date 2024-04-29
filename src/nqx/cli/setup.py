from typing import Annotated
from pathlib import Path
import os
import logging
import json

from rich import print
from rich.prompt import Prompt
import typer

from nqx.core import VenvProviderType, PythonProviderType
from nqx.providers import get_venv_provider
from nqx.utils import resolve_env_vars

from .config import get_config
from .app import app


@app.command()
def setup(
    yes: Annotated[
        bool,
        typer.Option(
            help="Skip the confirmation prompt.",
        ),
    ] = False,
):
    """
    Install this tool in the shell.
    """

    print("Setting up nqx...")

    config = get_config()
    venv_provider = VenvProviderType(config["venv_provider"])
    venv_provider = get_venv_provider()

    # Chose home folder
    nqx_home = Path(config["env"]["NQX_HOME"])
    current_env_home = os.environ.get("NQX_HOME", None)
    if current_env_home:
        nqx_home = Path(current_env_home)
    print()
    print(
        f"Chose a location for storing NQX related files. By default on this machine it will be : {nqx_home}"
    )
    new_nqx_home = Prompt.ask(
        r"Do you want to specify a different NQX_HOME? \[enter for default]"
    )

    if new_nqx_home:
        nqx_home = Path(new_nqx_home)
        config.set_env("NQX_HOME", str(nqx_home))

    custom_config = {}

    # Chose python provider
    python_provider = PythonProviderType(config["python_provider"])
    print()
    print("The default provider for Python installations is : ", python_provider)
    print("Possible choices are : ", ", ".join(PythonProviderType.__members__.keys()))
    new_python_provider = Prompt.ask(
        rf"Do you want to specify a different provider for Python installations? \[enter for {python_provider.value}]"
    )

    if new_python_provider:
        custom_config["python_provider"] = new_python_provider

    # Chose venv provider
    venv_provider = VenvProviderType(config["venv_provider"])
    print()
    print(
        "The default provider for Virtual Environment installations is : ",
        venv_provider,
    )
    print("Possible choices are : ", ", ".join(VenvProviderType.__members__.keys()))
    new_venv_provider = Prompt.ask(
        rf"Do you want to specify a different provider for Virtual Environment installations? \[enter for {venv_provider.value}]"
    )

    if new_venv_provider:
        custom_config["venv_provider"] = new_venv_provider

    # Write the config file
    logging.debug("Writing config file to %s", nqx_home)
    resolve_env_vars(nqx_home).mkdir(parents=True, exist_ok=True)
    if len(custom_config) > 0:
        with open(resolve_env_vars(nqx_home / "config.json"), "w") as f:
            json.dump(custom_config, f, indent=4)

    return 0
