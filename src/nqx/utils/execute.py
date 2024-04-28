import logging
import subprocess
import sys
import os

from .import_files import import_from_path

MODULE_HOME = os.environ.get("MODULESHOME", None)
if MODULE_HOME is not None:
    module = import_from_path(os.path.join(MODULE_HOME, "init/env_modules_python.py"))

old_python = sys.version_info.minor <= 6

if old_python:

    class FakeOut:
        def __init__(self, out):
            self.stdout = out


# Function to execute command or print it based on dry run
def execute(
    *args, dry_run=False, env=None, shell=False, capture_output=False, **kwargs
):
    logging.debug("Executing command: %s", " ".join(args))
    # executed_cmds.append(" ".join(args))

    if shell:
        args = (" ".join(args),)

    if not dry_run:
        if old_python:
            if capture_output:
                output = subprocess.check_output(args, env=env, shell=shell, **kwargs)
                output = FakeOut(output.decode("utf-8"))
                return output
            else:
                process = subprocess.run(args, env=env, shell=shell, **kwargs)
                return process
        else:
            process = subprocess.run(
                args, env=env, shell=shell, capture_output=capture_output, **kwargs
            )
        return process


def exec_module(
    *args,
    persist=False,
    dry_run=False,
    **kwargs,
):
    # executed_cmds.append("module " + " ".join(args))
    if dry_run:
        return
    if persist:
        args = " ".join(args)
        return subprocess.run(f"module {args}", shell=True)
    else:
        return module.module(*args, **kwargs)
