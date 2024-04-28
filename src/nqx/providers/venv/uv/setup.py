import os
import subprocess
import json
import shutil
import logging

import typer

from nqx.core import EnvConfig, EnvType
from nqx.cli.config import get_config
from nqx.utils import execute, resolve_env_vars

UV_BIN = resolve_env_vars("$HOME/.cargo/bin/uv")


def is_installed():
    return os.path.exists(UV_BIN)


def install(verbose=False):
    execute("curl -LsSf https://astral.sh/uv/install.sh | sh")


def create_env(name, pkg, venv_depot: str, *, environment: EnvConfig, force=False, process=None):
    venv_depot = resolve_env_vars(venv_depot)
    venv_path = venv_depot / name

    if not venv_path.exists():
        venv_path.mkdir(parents=True, exist_ok=False)
    else:
        if force:
            shutil.rmtree(venv_path)
            venv_path.mkdir()
        else:
            print(f"Virtual environment {venv_path} already exists")
            raise typer.Exit()

    logging.debug("Creating virtual environment %s", venv_path)
    result = subprocess.run([UV_BIN, "venv", "."], cwd=venv_path, env=environment.env)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create virtual environment {name}")
    
    environment.env["VIRTUAL_ENV"] = str(venv_path)
    return environment

def activate_env(name : str, venv_depot: str, *, environment: EnvConfig):
    venv_depot = resolve_env_vars(venv_depot)
    venv_path = venv_depot / name

    if not venv_path.exists():
        print(f"Virtual environment {venv_path} does not exist")
        raise typer.Exit(1)
    
    # Set the virtual env and path in the environment
    environment.env["VIRTUAL_ENV"] = str(venv_path)
    environment.env["PATH"] = str(venv_path / "bin") + ":" + environment.env.get("PATH", "")
    return environment

def remove_env(name, venv_depot):
    venv_depot = resolve_env_vars(venv_depot)
    venv_path = venv_depot / name

    if not venv_path.exists():
        print(f"Virtual environment {venv_path} does not exist")
        raise typer.Exit(1)

    logging.debug("Removing virtual environment %s", venv_path)
    return shutil.rmtree(venv_path)


def list_envs(venv_depot):
    venv_depot = resolve_env_vars(venv_depot)
    logging.debug("Listing virtual environments in %s", venv_depot)

    if not os.path.exists(venv_depot):
        logging.debug("No virtual environments found in %s", venv_depot)
        return []

    dirs = os.listdir(venv_depot)
    envs = []
    for d in dirs:
        if os.path.isdir(venv_depot / d):
            env_name = os.path.basename(d)
            envs.append((env_name, venv_depot / d))

            # if (venv_depot / d / ".venv").exists():
            #     env_name = os.path.basename(d)
            #     envs.append((env_name, venv_depot / d))
            # else:
            #     logging.debug("Skipping %s, not a virtual environment", d)
    return envs


def read_env_config(name, venv_depot) -> dict:
    venv_depot = resolve_env_vars(venv_depot)
    venv_path = venv_depot / name

    if not venv_path.exists():
        raise FileNotFoundError(f"Virtual environment {venv_path} does not exist")

    settings_file = venv_path / "nqx_config.json"
    if settings_file.exists():
        with open(settings_file, "r") as f:
            return json.load(f)
    return {}

def write_env_config(name, config: dict, venv_depot):
    venv_depot = resolve_env_vars(venv_depot)
    venv_path = venv_depot / name

    if not venv_path.exists():
        raise FileNotFoundError(f"Virtual environment {venv_path} does not exist")

    with open(venv_path / "nqx_config.json", "w") as f:
        json.dump(config, f)
    return config

def set_env_type(name, type: EnvType, venv_depot):
    config = read_env_config(name, venv_depot)
    config['type'] = type.value
    write_env_config(name, config, venv_depot)

def get_env_type(name, venv_depot) -> EnvType:
    config = read_env_config(name, venv_depot)
    return EnvType(config.get('type', None))


def install_packages(name, file, venv_depot, *, environment: EnvConfig):
    config = get_config()
    venv_depot = resolve_env_vars(venv_depot)
    venv_path = venv_depot / name

    if not venv_path.exists():
        raise FileNotFoundError(f"Virtual environment {venv_path} does not exist")

    if not os.path.exists(file):
        raise FileNotFoundError(f"Requirements file {file} does not exist")

    # set the env for uv
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_path)
    logging.debug("Installing packages in virtual environment VIRTUAL_ENV=%s , for file %s", venv_path, str(file))
    args = []
    if config["verbose"]:
        args.append("-v")
    result = subprocess.run([UV_BIN, "pip", "install", *args, "-r", str(file)], env=env, capture_output=True, cwd=venv_path)
    if result.returncode != 0:
        print("Installation failed because of an internal error of UV")
        print("==============================================")
        print(result.stdout.decode("utf-8"))
        print("==============================================")
        print(result.stderr.decode("utf-8"))
        print("==============================================")
        raise RuntimeError(f"Failed to install packages in virtual environment {name}")
    return result