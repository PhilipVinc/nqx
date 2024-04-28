#!/usr/bin/python3
import argparse
import sys
import os
import subprocess
import logging
import json


## -- UTILITIES
VERBOSE = False
logger = logging.getLogger(__name__)
executed_cmds = []

startup_file_teamplate = """
def _load_modules():
    import importlib, os
    MODULE_HOME = '{}'
    path = os.path.join(MODULE_HOME, "init/env_modules_python.py")
    spec = importlib.util.spec_from_file_location("module.name", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mod = module.module

    pkgs = [{}]
    for pkg in pkgs:
        mod("load", pkg)
    return 
_load_modules()
del _load_modules
"""


MODULE_HOME = os.environ.get("MODULESHOME", None)
module = import_from_path(os.path.join(MODULE_HOME, "init/env_modules_python.py"))


def exec_module(
    *args,
    persist=False,
    dry_run=False,
    **kwargs,
):
    executed_cmds.append("module " + " ".join(args))
    if dry_run:
        return
    if persist:
        args = " ".join(args)
        return subprocess.run(f"module {args}", shell=True)
        # return os.system(f"module {args}")
    else:
        return module.module(*args, **kwargs)


# Function to execute command or print it based on dry run
def execute(
    *args, dry_run=False, env=None, shell=False, capture_output=False, **kwargs
):
    logger.debug("Executing command: %s", " ".join(args))
    executed_cmds.append(" ".join(args))

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


# Function to install package from specified source or version
def install_package(
    package_name, extras=(), upgrade=True, version=None, env=None, dry_run=False
):
    package_info = packages.get(package_name)
    if not package_info:
        logger.error(
            f"Error: Package '{package_name}' not found in packages dictionary."
        )
        sys.exit(1)

    # handle extras
    if isinstance(extras, str):
        extras = (extras,)
    real_package_name = package_info.get("name", package_name)
    if len(extras) > 0:
        package_install_str = f"{real_package_name}[{','.join(extras)}]"
    else:
        package_install_str = real_package_name

    # handle version
    if version is None:
        version = package_info.get("default_version", None)
    if version.lower() == "latest":
        version = None
    if version is not None:
        if version == "master" or version == "main":
            github_repo = package_info.get("github_repo", None)
            if github_repo is None:
                logger.error(
                    "Error: GitHub repository name not provided for 'master' version."
                )
                sys.exit(1)
            if len(extras) > 0:
                raise NotImplemented
            else:
                package_install_str = f"git+https://github.com/{github_repo}.git"
        else:
            package_install_str = f"{package_install_str}=={version}"

    # add index url if provided
    index_install_str = package_info.get("index_url", None)
    if index_install_str is not None:
        index_install_str = (f"-f {index_install_str}",)
    else:
        index_install_str = ()

    flags = []
    if upgrade:
        flags.append("--upgrade")
    flags = tuple(flags)

    execute(
        "conda",
        "run",
        "-n",
        env,
        "pip",
        "install",
        *flags,
        package_install_str,
        *index_install_str,
        dry_run=dry_run,
    )


def get_env_path(env_name):
    res = execute("conda", "env", "list", "--json", capture_output=True)
    envs = json.loads(res.stdout)["envs"]
    for env_path in envs:
        path, name = os.path.split(env_path)
        if name == env_name:
            return env_path
    return None


def get_env_type(env_name, env_path=None):
    if env_path is None:
        env_path = get_env_path(env_name)
    nqx_file_path = os.path.join(env_path, ".nqx")
    if os.path.isfile(nqx_file_path):
        with open(os.path.join(env_path, ".nqx"), "r") as f:
            data = json.load(f)
            return data.get("type", None)
    else:
        return "?"


## -- END UTILTIIES

## CREATE ENVIRONMENT
packages = {
    "netket": {
        "name": "netket",
        "default_version": "master",
        "github_repo": "netket/netket",
    },
    "mpi4py": {
        "name": "mpi4py",
        "default_version": "latest",
    },
    "mpi4jax": {
        "name": "mpi4jax",
        "default_version": "latest",
        "github_repo": "mpi4jax/mpi4jax",
    },
    "jax": {
        "name": "jax",
        "default_version": None,
        "github_repo": "google/jax",
    },
    "jax-gpu": {
        "name": "jax",
        "default_version": None,
        "github_repo": "google/jax",
        "index_url": "https://storage.googleapis.com/jax-releases/jax_releases.html",
    },
}


def make_create_parser(subparsers):
    parser = subparsers.add_parser(
        "create", help="Create a new Python environment setup for netket usage."
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Name of the new environment.",  # required=True
    )
    parser.add_argument(
        "name",
        nargs="?",
        type=str,
        help="Name of the new environment.",  # required=True
    )
    parser.add_argument(
        "--type",
        type=str,
        help="Type of the new environment.",
        choices=["cpu", "gpu", "gpu-mpi"],
        # required=True,
    )
    parser.add_argument(
        "type",
        nargs="?",
        type=str,
        help="Type of the new environment.",
        choices=["cpu", "gpu", "gpu-mpi"],
        # required=True,
    )
    parser.add_argument(
        "--python",
        type=str,
        help="Version of Python to be used",
        default="3.11",
        metavar="3.XX",
    )
    parser.add_argument(
        "--netket",
        type=str,
        help="Version of NetKet to be used",
        default="master",
        metavar="3.X.Y | master",
    )

    parser.add_argument(
        "--jax",
        type=str,
        help="Version of jax to be used",
        default="latest",
        metavar="0.4.Y | master",
    )

    parser.add_argument(
        "--dry-run",
        "--dry",
        action="store_true",
        help="Do not create the environment, just print the commands.",
        default=False,
    )
    parser.add_argument(
        "--skip-create",
        action="store_true",
        help="Do not create the environment, just install the packages.",
        default=False,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output.", default=False
    )
    return parser


def command_create_env(parser, args):
    # Validate if name and type were defined
    if args.name is None or args.type is None:
        parser.error("Both 'name' and 'type' arguments are required.")

    global DRY_RUN
    DRY_RUN = args.dry_run
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # load mambaforge
    exec_module("load", "mambaforge")
    env = os.environ.copy()

    # Create the environment
    opts = [
        "--yes",
        "--name",
        args.name,
    ]
    if not args.skip_create:
        execute(
            "mamba",
            "create",
            *opts,
            f"python={args.python}",
            shell=True,
            env=env,
            dry_run=args.dry_run,
        )
    # execute("mamba create", *opts, f"python={args.python}",  shell=True, env=env, dry_run=args.dry_run)
    logger.info("Succesfully created the environment. Now installing packages.")

    # Install relevant packages using pip
    if args.type == "cpu":
        exec_module("load", "gcc/10.2.0", "openmpi/4.1.4")
        modules = ["gcc/10.2.0", "openmpi/4.1.4"]

        install_package(
            "jax", extras="cpu", version=args.jax, env=args.name, dry_run=args.dry_run
        )
        install_package(
            "netket", version=args.netket, env=args.name, dry_run=args.dry_run
        )
        install_package("mpi4jax", env=args.name, dry_run=args.dry_run)
    elif args.type == "gpu":
        modules = []

        install_package(
            "jax-gpu",
            extras="cuda12_pip",
            version=args.jax,
            env=args.name,
            dry_run=args.dry_run,
        )
        install_package(
            "netket", version=args.netket, env=args.name, dry_run=args.dry_run
        )
    elif args.type == "gpu-mpi":
        exec_module("load", "gcc/10.2.0", "openmpi/4.1.4", "cuda", "cudnn")
        modules = ["gcc/10.2.0", "openmpi/4.1.4", "cuda", "cudnn"]

        install_package(
            "jax-gpu",
            extras="cuda12_local",
            version=args.jax,
            env=args.name,
            dry_run=args.dry_run,
        )
        install_package(
            "netket", version=args.netket, env=args.name, dry_run=args.dry_run
        )

    # write a small flag file to the environment
    env_path = get_env_path(args.name)
    if not args.dry_run:
        fpath = os.path.join(env_path, ".nqx")
        logger.debug("writing to file %s", fpath)
        with open(fpath, "w") as f:
            f.write(json.dumps({"type": args.type}))

    # Create a startup file
    modules.append("mambaforge")
    startup_file = startup_file_teamplate.format(
        MODULE_HOME, ", ".join([f'"{pkg}"' for pkg in modules])
    )
    if not args.dry_run:
        fpath = os.path.join(env_path, "nqx_startup.py")
        logger.debug("writing to file %s", fpath)
        with open(fpath, "w") as f:
            f.write(startup_file)

    return


## END CREATE ENVIRONMENT


def main():
    parser = argparse.ArgumentParser(
        description="Neural Quantum Group @ X utilities for Cholesky HPC"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")
    subparser_create = make_create_parser(subparsers)
    subparser_list = make_list_parser(subparsers)
    subparser_activate = make_activate_parser(subparsers)

    # run
    args = parser.parse_args()

    if args.command == "create":
        command_create_env(subparser_create, args)
    elif args.command == "list":
        command_list_env(subparser_list, args)
    elif args.command == "activate":
        command_activate_env(subparser_activate, args)
    else:
        print("Invalid subcommand")
        parser.print_help(sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
