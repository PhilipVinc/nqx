from typing import Annotated
import logging

import typer

from .config import get_config

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main(
    verbose: Annotated[bool, typer.Option(help="Verbose output")] = False,
    debug: Annotated[bool, typer.Option(help="Debug output")] = False,
):
    """
    CLI for everything related to the Neural Quantum Group @ X.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    config = get_config()
    config["verbose"] = verbose
    config["debug"] = debug

    config["app_dir"] = typer.get_app_dir("NQX")
    logging.debug("app dir: %s", config["app_dir"])
