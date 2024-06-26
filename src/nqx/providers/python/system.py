import subprocess

import typer

from nqx.core import EnvConfig


def _is_command_available(command):
    try:
        subprocess.run(
            [command, "--version"],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_env_with_python(env: EnvConfig):
    if _is_command_available("python"):
        return env
    else:
        print(
            "Python is not available in the environment. Please ensure that Python is installed in the environment."
        )
        raise typer.Exit(1)
