import os
import subprocess
import logging
import sys

from pathlib import Path

from rich import print

from nqx.core import EnvConfig

import typer

PYTHON_MODULEFILES_INIT = [
    "init/env_modules_python.py",
    "init/python.py",
]


def is_available():
    """
    Check if the `module` command is available in the shell.
    """
    MODULESHOME = os.environ.get("MODULESHOME", None)
    if MODULESHOME is None or not os.path.exists(MODULESHOME):
        return False
    MODULESHOME = Path(MODULESHOME)

    for init_file in PYTHON_MODULEFILES_INIT:
        if (MODULESHOME / init_file).exists():
            return True
    return False


def load_modules(*module_names: str, environment: EnvConfig):
    """
    Load one or more modules in the specified environment.

    This uses the `module load` command to load the modules in the specified environment.
    """
    return execute_module_in_env("load", *module_names, environment=environment)


load = load_modules


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
        raise FileNotFoundError("MODULESHOME is not set or does not exist.")

    MODULESHOME = Path(MODULESHOME)
    logging.debug("MODULESHOME: %s", MODULESHOME)

    logging.debug(
        "Scanning for the required module init file in the MODULESHOME directory."
    )
    MODULES_INIT_FILE = None
    for init_file in PYTHON_MODULEFILES_INIT:
        logging.debug("Checking for the file: %s", str(MODULESHOME / init_file))
        if (MODULESHOME / init_file).exists():
            logging.debug(
                f"Found the required file {init_file} in the MODULESHOME directory."
            )
            MODULES_INIT_FILE = MODULESHOME / init_file
            break
    if MODULES_INIT_FILE is None:
        print(
            "Could not find the required module init file in the MODULESHOME directory."
        )
        print("I checked the following paths:")
        for init_file in PYTHON_MODULEFILES_INIT:
            print(MODULESHOME / init_file)
        raise FileNotFoundError(
            "Could not find the required module init file in the MODULESHOME directory."
        )

    # Create a copy of the current environment variables dictionary
    env = environment.env

    # Create a separate Python interpreter with the updated environment
    python_interpreter = subprocess.Popen(
        [sys.executable, "-i", str(MODULES_INIT_FILE)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    logging.debug("Started subshell using the python interpreter %s", sys.executable)

    # Execute the command '$MODULESHOME/init/python.py' in the separate interpreter
    # init_command = str(MODULESHOME / "init/python.py") + "\n"
    # python_interpreter.stdin.write(init_command.encode())
    # python_interpreter.stdin.flush()
    # output = python_interpreter.stdout.readline().decode()
    # logging.debug("Output of modules init command: %s", output.strip())

    # Execute the user-provided command in the separate interpreter
    modules_command = [f'"{module}"' for module in modules_command]
    command = ", ".join(modules_command)
    command = f"module({command})\n"
    python_interpreter.stdin.write(command.encode())
    python_interpreter.stdin.flush()
    logging.debug("Executed command to load modules: %s", command.strip())
    output = python_interpreter.stdout.readline().decode()
    logging.debug("Output of modules load command: %s", output.strip())

    # exfiltrate the environment configuration
    # copy to convert it to a plain dict
    command = "import os; print(os.environ.copy());\n"
    python_interpreter.stdin.write(command.encode())
    python_interpreter.stdin.flush()
    logging.debug("Executed command to get environment: %s", command.strip())
    output = python_interpreter.stdout.readline().decode()
    output = output.strip()

    # Parse the output of the command to get the environment dictionary
    new_env = eval(output)

    # Close the separate interpreter
    python_interpreter.stdin.close()
    python_interpreter.wait()

    if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
        # print new env variables
        for key, value in new_env.items():
            if key not in env or env[key] != value:
                logging.debug(f"ADDED NEW ENV KEY: {key}={value}")

    # Return the environment dictionary after executing the command
    return EnvConfig(env=new_env)


def generate_module_script(*modules_command: tuple[str, ...], environment: EnvConfig):
    """
    Executes a modules command in an environment.

    This spawns a subpython shell.

    This uses the `module ***` command to load the modules in the specified environment.
    """
    if len(modules_command) == 0:
        return ""

    MODULESHOME = os.environ.get("MODULESHOME", None)
    if MODULESHOME is None or not os.path.exists(MODULESHOME):
        print(
            "MODULESHOME is not set or does not exist. Please set MODULESHOME to the path of the modules directory."
        )
        typer.Exit(1)

    MODULESHOME = Path(MODULESHOME)

    MODULES_INIT_FILE = None
    for init_file in PYTHON_MODULEFILES_INIT:
        if (MODULESHOME / init_file).exists():
            MODULES_INIT_FILE = MODULESHOME / init_file
            break
    if MODULES_INIT_FILE is None:
        raise FileNotFoundError(
            "Could not find the required module init file in the MODULESHOME directory."
        )

    # Create a copy of the current environment variables dictionary
    modules_command = [f'"{module}"' for module in modules_command]

    # Create a separate Python interpreter with the updated environment
    script = []
    script.append("import os")
    script.append(f"_path = {str(MODULES_INIT_FILE)}")
    script.append("with open(_path, 'r') as f:")
    script.append("    exec(f.read())")
    script.append(f"module('load', {', '.join(modules_command)})")
    script.append("")

    return "\n".join(script)
