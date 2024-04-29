from nqx.core import EnvConfig

import typer

from .. import modules


def is_available():
    return modules.is_available()


def get_env_with_python(env: EnvConfig):
    if not is_available():
        print(
            "The module command is not available in the environment. Cannot use python provider."
        )
        raise typer.Exit(1)

    modules.execute_module_in_env("load", "python", environment=env)
    return env
