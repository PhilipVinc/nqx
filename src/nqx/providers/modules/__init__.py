import os
import subprocess
import logging

from pathlib import Path

from rich import print

from nqx.core import EnvConfig

import typer


def load_modules(*module_names: str, environment: EnvConfig):
    """
    Load one or more modules in the specified environment.

    This uses the `module load` command to load the modules in the specified environment.
    """
    return execute_module_in_env("load", *module_names, environment=environment)


def execute_module_in_env(*modules_command: tuple[str, ...], environment: EnvConfig):
    """
    Executes a modules command in an environment.

    This spawns a subpython shell.

    This uses the `module ***` command to load the modules in the specified environment.
    """

    MODULESHOME = os.environ.get("MODULESHOME", None)
    if MODULESHOME is None or not os.path.exists(MODULESHOME):
        print(
            "MODULESHOME is not set or does not exist. Please set MODULESHOME to the path of the modules directory."
        )
        typer.Exit(1)
    MODULESHOME = Path(MODULESHOME)

    # Create a copy of the current environment variables dictionary
    env = environment.env

    # Create a separate Python interpreter with the updated environment
    python_interpreter = subprocess.Popen(
        ["python"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    # Execute the command '$MODULESHOME/init/python.py' in the separate interpreter
    init_command = str(MODULESHOME / "init/python.py") + "\n"
    python_interpreter.stdin.write(init_command.encode())
    python_interpreter.stdin.flush()
    output = python_interpreter.stdout.readline().decode()
    logging.debug("Output of modules init command: %s", output.strip())

    # Execute the user-provided command in the separate interpreter
    command = " ".join(modules_command) + "\n"
    python_interpreter.stdin.write(command.encode())
    python_interpreter.stdin.flush()
    output = python_interpreter.stdout.readline().decode()
    logging.debug("Output of modules load command: %s", output.strip())

    # exfiltrate the environment configuration
    command = "import os; print(os.environ);\n"
    python_interpreter.stdin.write(command.encode())
    python_interpreter.stdin.flush()
    output = python_interpreter.stdout.readline().decode()
    output = output.strip()

    # Parse the output of the command to get the environment dictionary
    new_env = eval(output)

    # Close the separate interpreter
    python_interpreter.stdin.close()
    python_interpreter.wait()

    # Return the environment dictionary after executing the command
    return EnvConfig(env=new_env)
