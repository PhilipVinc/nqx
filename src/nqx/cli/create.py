from typing import Annotated
from pathlib import Path
import shutil
import os
import logging
import json
import re

from rich import print
import typer

from nqx.core import EnvConfig, EnvType, VenvProviderType
from nqx.providers import get_venv_provider, get_python_provider, modules

from .config import get_config, get_requirements_file_for_type
from .app import app


@app.command(no_args_is_help=True)
def create(
    name: Annotated[str, typer.Argument(help="The name of the environment.")],
    type: Annotated[
        EnvType, typer.Argument(help="Type of the new environment.")
    ] = EnvType.cpu,
    *,
    dry_run: Annotated[
        bool,
        typer.Option(help="Do not create the environment, just print the commands."),
    ] = False,
    skip_create: Annotated[
        bool, typer.Option(help="Skip the creation of the environment.")
    ] = False,
    kernel: Annotated[
        bool,
        typer.Option(help="Create the iPyKernel kernel for the environment."),
    ] = True,
    provider: Annotated[
        VenvProviderType, typer.Option(help="The provider to use for the environment.")
    ] = VenvProviderType.auto,
    force: Annotated[bool, typer.Option(help="Force override.")] = False,
):
    """
    Create a new environment with NAME of type TYPE
    """
    config = get_config()

    # Create EnvConfig
    env_config = EnvConfig(env=os.environ.copy())

    ###############################################################
    # Get Python
    python_provider = get_python_provider()

    env_config = python_provider.get_env_with_python(env_config)

    ###############################################################
    # Create the virtual environment
    if provider is VenvProviderType.auto:
        provider = VenvProviderType(config["venv_provider"])

    provider = get_venv_provider(provider)
    venv_depot = config["venv_location"]

    if not skip_create:
        env_config = provider.create_env(
            name, type, venv_depot=venv_depot, force=force, environment=env_config
        )
    else:
        print("Skipping environment creation")
        env_config = provider.activate_env(
            name, venv_depot=venv_depot, environment=env_config
        )

    ###############################################################
    # Write the nqx tag file to store the env type
    provider.set_env_type(name, type, venv_depot)

    ###############################################################
    # Setup env variables
    env_config.update(config["configurations"][type.value].get("env", {}))

    ###############################################################
    # Setup modules
    modules_to_load = config["configurations"][type.value].get("modules", [])
    if len(modules_to_load) > 0:
        logging.debug("Loading modules")
        env_config = modules.load_modules(*modules_to_load, environment=env_config)

    ###############################################################
    # Install python packages
    # get dependencies
    file_subpath = config["configurations"][type.value]["requirements"]
    requirements_file = get_requirements_file_for_type(file_subpath)

    if not os.path.exists(requirements_file):
        print(f"Requirements file {requirements_file} does not exist")
        typer.Exit(1)

    # install packages using pip
    print("installing packages")
    provider.install_packages(
        name, file=requirements_file, venv_depot=venv_depot, environment=env_config
    )
    print("installed")

    ###############################################################
    # Create the iPyKernel kernel
    if kernel:
        print("Creating kernel")
        provider.install_packages(
            name, "ipykernel", venv_depot=venv_depot, environment=env_config
        )
        result = provider.run_python_command(
            name,
            [
                "-m",
                "ipykernel",
                "install",
                "--user",
                "--name",
                name,
                "--display-name",
                f"NQX:Python ({name})",
            ],
            venv_depot=venv_depot,
            environment=env_config,
            capture_output=True,
        )

        output = result.stdout.decode("utf-8").strip()

        match = re.search(r"in (.*)", output)
        if match:
            base_path = match.group(1)
            logging.debug("Kernel installed in %s", base_path)

        base_path = Path(base_path)

        script_path = base_path / "launch_kernel"
        with open(script_path, "w") as f:
            f.write(modules.generate_module_bash_script(*modules_to_load, environment=env_config))
        
        os.chmod(str(script_path), os.stat(str(script_path)).st_mode | 0o111)



        # script = modules.generate_module_script(
        #     *modules_to_load, environment=env_config
        # )
        # with open(base_path / "startup.py", "w") as f:
        #     f.write(script)

        kernel_path = base_path / "kernel.json"
        with open(kernel_path) as f:
            kernel_config = json.load(f)
        _env = kernel_config.get("env", {})
        #_env["PYTHONSTARTUP"] = str(base_path / "startup.py")
        _env["MODULESHOME"] = os.environ.get("MODULESHOME", "")
        _env["MODULEPATH"] = os.environ.get("MODULEPATH", "")
        kernel_config["env"] = _env

        kernel_config["argv"] = [str(script_path)] + kernel_config["argv"]
        with open(kernel_path, "w") as f:
            json.dump(kernel_config, f)
        print("edited kernel at ", kernel_path)


@app.command(no_args_is_help=True)
def remove(
    name: Annotated[str, typer.Argument(help="The name of the environment to delete.")],
):
    """
    Remove an environment
    """
    config = get_config()

    provider = config["venv_provider"]

    venv_depot = Path(config["venv_location"])
    provider = get_venv_provider(provider)

    provider.remove_env(name, venv_depot=venv_depot)
    print(f"Environment {name} removed")

    # final cleanup
    path = venv_depot / name
    if path.exists():
        shutil.rmtree(path)
    return 0
