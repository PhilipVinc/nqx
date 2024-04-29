import os
import subprocess
import logging
import sys
import tempfile

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


# def execute_module_in_env(*modules_command: tuple[str, ...], environment: EnvConfig):
#     """
#     Executes a modules command in an environment.

#     This spawns a subpython shell.

#     This uses the `module ***` command to load the modules in the specified environment.
#     """

#     MODULESHOME = os.environ.get("MODULESHOME", None)
#     if MODULESHOME is None or not os.path.exists(MODULESHOME):
#         print(
#             "MODULESHOME is not set or does not exist. Please set MODULESHOME to the path of the modules directory."
#         )
#         typer.Exit(1)
#         raise FileNotFoundError("MODULESHOME is not set or does not exist.")

#     MODULESHOME = Path(MODULESHOME)
#     logging.debug("MODULESHOME: %s", MODULESHOME)

#     logging.debug(
#         "Scanning for the required module init file in the MODULESHOME directory."
#     )
#     MODULES_INIT_FILE = None
#     for init_file in PYTHON_MODULEFILES_INIT:
#         logging.debug("Checking for the file: %s", str(MODULESHOME / init_file))
#         if (MODULESHOME / init_file).exists():
#             logging.debug(
#                 f"Found the required file {init_file} in the MODULESHOME directory."
#             )
#             MODULES_INIT_FILE = MODULESHOME / init_file
#             break
#     if MODULES_INIT_FILE is None:
#         print(
#             "Could not find the required module init file in the MODULESHOME directory."
#         )
#         print("I checked the following paths:")
#         for init_file in PYTHON_MODULEFILES_INIT:
#             print(MODULESHOME / init_file)
#         raise FileNotFoundError(
#             "Could not find the required module init file in the MODULESHOME directory."
#         )

#     # Create a copy of the current environment variables dictionary
#     env = environment.copy().env
#     env["MODULESHOME"] = str(MODULESHOME)
#     env["MODULEPATH"] = os.environ.get("MODULEPATH")
#     env["MODULEPATH_modshare"] = os.environ.get("MODULEPATH_modshare")

#     # Create a separate Python interpreter with the updated environment
#     # python_interpreter = subprocess.Popen(
#     #     [sys.executable, "-i", str(MODULES_INIT_FILE)],
#     #     stdin=subprocess.PIPE,
#     #     #stdout=subprocess.PIPE,
#     #     #stderr=subprocess.PIPE,
#     #     shell=True,
#     #     env=env,
#     # )
#     # logging.debug("Started subshell using the python interpreter %s", sys.executable)

#     # # Execute the command '$MODULESHOME/init/python.py' in the separate interpreter
#     # # init_command = str(MODULESHOME / "init/python.py") + "\n"
#     # # python_interpreter.stdin.write(init_command.encode())
#     # # python_interpreter.stdin.flush()
#     # # output = python_interpreter.stdout.readline().decode()
#     # # logging.debug("Output of modules init command: %s", output.strip())

#     # # Execute the user-provided command in the separate interpreter
#     modules_command = [f'"{module}"' for module in modules_command]
#     command = ", ".join(modules_command)
#     # command = f"module({command})\n"
#     # python_interpreter.stdin.write(command.encode())
#     # python_interpreter.stdin.flush()
#     # logging.debug("Executed command to load modules: %s", command.strip())
#     # #output = python_interpreter.stdout.readline().decode()
#     # #logging.debug("Output of modules load command: %s", output.strip())

#     # # exfiltrate the environment configuration
#     # # copy to convert it to a plain dict
#     # command = "import os; print(os.environ.copy());\n"
#     # python_interpreter.stdin.write(command.encode())
#     # python_interpreter.stdin.flush()
#     # logging.debug("Executed command to get environment: %s", command.strip())
#     # #output = python_interpreter.stdout.readline().decode()
#     # #output = output.strip()

#     # # Close the separate interpreter
#     # python_interpreter.stdin.close()
#     # python_interpreter.wait()

#     with open(MODULES_INIT_FILE, "r") as f:
#         script = [f.read()]
#     script.append(f"module({command})")
#     script.append("import os")
#     script.append("print(os.environ.copy())")

#     logging.debug("executing python to extract the env variables")
#     logging.debug("python script contains: %s", script)
#     with tempfile.TemporaryDirectory() as temp_dir:
#         temp_file_path = os.path.join(temp_dir, 'python.py')

#         # Write data to the temporary file
#         with open(temp_file_path, 'w') as temp_file:
#             temp_file.write("\n".join(script))

#         result = subprocess.run(
#             [sys.executable, temp_file_path],
#             capture_output=True,
#             env=env,
#             )

#     # Parse the output of the command to get the environment dictionary
#     output = result.stdout.decode("utf-8").strip()
#     new_env = eval(output)

#     logging.debug("Parsing env variables of which there are %i", len(new_env))
#     if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
#         # print new env variables
#         for key, value in new_env.items():
#             if key not in env or env[key] != value:
#                 logging.debug(f"ADDED NEW ENV KEY: {key}={value}")

#     # Return the environment dictionary after executing the command
#     return EnvConfig(env=new_env)


def generate_module_python_script(*modules_command: tuple[str, ...], environment: EnvConfig):
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


def generate_module_bash_script(*modules_command: tuple[str, ...], environment: EnvConfig):
    """
    Executes a modules command in an environment.

    This spawns a subpython shell.

    This uses the `module ***` command to load the modules in the specified environment.
    """
    if len(modules_command) == 0:
        return ""

    # Create a copy of the current environment variables dictionary
    modules_command = ["module", "load", ] + list(modules_command)

    # Create a separate Python interpreter with the updated environment
    script = ["#!/bin/bash"]
    script.append(" ".join(modules_command))
    script.append("\"$@\"")
    script.append("")

    return "\n".join(script)


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
    env = environment.copy().env
    env["MODULESHOME"] = str(MODULESHOME)
    env["MODULEPATH"] = os.environ.get("MODULEPATH")
    env["MODULEPATH_modshare"] = os.environ.get("MODULEPATH_modshare")

    modules_command = ["module"] + list(modules_command)
    modules_command = " ".join(modules_command)

    magic_string = "!!!NQX!!!NQX!!!NQX!!!"
    script = []
    script.append(modules_command)
    script.append(f'echo "{magic_string}"')
    script.append(f'{sys.executable} -c "import os; print(os.environ.copy());"')
    script = " && ".join(script)

    logging.debug("executing python to extract the env variables")
    logging.debug("python script contains: %s", script)

    result = subprocess.run([script], capture_output=True, env=env, shell=True)

    # Parse the output of the command to get the environment dictionary
    erroutput = result.stderr.decode("utf-8").strip()
    logging.debug("Got error output message %s", erroutput)
    output = result.stdout.decode("utf-8").strip()
    # logging.debug("Got output message %s", output)
    parts = output.split(magic_string)
    new_env = eval(parts[1])

    logging.debug("Parsing env variables of which there are %i", len(new_env))
    if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
        # print new env variables
        for key, value in new_env.items():
            if key not in env or env[key] != value:
                logging.debug(f"ADDED NEW ENV KEY: {key}={value}")

    # Return the environment dictionary after executing the command
    return EnvConfig(env=new_env)
