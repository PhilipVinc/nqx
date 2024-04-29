from typing import Annotated
import os
import logging

from rich import print
import typer

from nqx.core import EnvConfig, VenvProviderType
from nqx.providers import get_venv_provider, get_python_provider

from .config import get_config
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
    # Check if a nqx environment is already loaded. In which case,
    # we need to deactivate it first
    current_env = os.environ.get("NQX_ENV", None)
    if current_env is not None:
        deactivate()

    ###############################################################
    # Get Python : not needed for activating the environment as
    # it is set by the virtualenv activation script
    python_provider = get_python_provider()
    env_config = python_provider.get_env_with_python(env_config)

    ###############################################################
    # Create the virtual environment
    provider = get_venv_provider(VenvProviderType(config["venv_provider"]))
    venv_depot = config["venv_location"]
    env_config = provider.activate_env(
        name, venv_depot=venv_depot, environment=env_config
    )

    ###############################################################
    # Setup env variables
    type = provider.get_env_type(name, venv_depot)
    env_config.update(config["configurations"][type.value].get("env", {}))

    ###############################################################
    #
    for k, v in env_config.env.items():
        print(f'export {k}="{v}"')
    print(f'export NQX_ENV="{name}"')

    ###############################################################
    # Setup modules
    modules_to_load = config["configurations"][type.value].get("modules", [])
    logging.debug("Must load modules: %s", modules_to_load)
    if len(modules_to_load) > 0:
        logging.debug("Loading modules")
        # env_config = modules.load_modules(*modules_to_load, environment=env_config)
        cmd = "module load " + " ".join(modules_to_load)
        print(cmd)

    # PS1
    ps1 = os.getenv("PS1", "")
    if "POWERLINE_COMMAND" in ps1:
        # defer
        pass
    else:
        print("""export _NQX_PS1_BACKUP="$PS1" """)
        print(f"""PS1="(nqx:{name}) $PS1" """)


@app.command()
def deactivate():
    """
    Disable the current environment
    """
    config = get_config()

    # Create EnvConfig
    # env_config = EnvConfig(env={})

    ###############################################################
    # Get Python : not needed for activating the environment as
    # it is set by the virtualenv activation script
    # python_provider = get_python_provider()
    # env_config = python_provider.get_env_with_python(env_config)

    ###############################################################
    # Create the virtual environment
    provider = get_venv_provider(VenvProviderType(config["venv_provider"]))
    venv_depot = config["venv_location"]
    disable_lines = provider.deactivate_env(venv_depot)
    for line in disable_lines:
        print(line)

    ###############################################################
    # remove env variables
    # Check what is the current environment
    current_env = os.environ.get("NQX_ENV", None)

    if current_env is not None:
        type = provider.get_env_type(current_env, venv_depot)
        env_variables = config["configurations"][type.value].get("env", {})
        for k in env_variables.keys():
            print(f"unset {k}")
        print("unset NQX_ENV")

        ###############################################################
        # unload modules
        modules_to_load = config["configurations"][type.value].get("modules", [])
        if len(modules_to_load) > 0:
            # env_config = modules.load_modules(*modules_to_load, environment=env_config)
            cmd = "module unload " + " ".join(modules_to_load)
            print(cmd)

    # psi1
    ps1 = os.getenv("PS1", "")
    old_psi1 = os.getenv("_NQX_PS1_BACKUP", None)
    if "POWERLINE_COMMAND" in ps1:
        # defer
        pass
    elif old_psi1 is not None:
        print("""PS1="$_NQX_PS1_BACKUP" """)
