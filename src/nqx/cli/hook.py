from typing import Annotated
from pathlib import Path
import os
import shutil
import logging

from rich import print
import typer


from .app import app


@app.command()
def hook():
    """
    List all environments
    """
    config_dir = Path(os.environ["NQX_INTERNAL_CONFIG"])

    with open(config_dir / "nqx.sh") as f:
        bash_config = f.read()

    nqx_exe = shutil.which("nqx")
    bash_config = f"export NQX_EXE='{nqx_exe}'\n" + bash_config

    print(bash_config)

    return 0


setup_block_template = """
__nqx_setup="$('{}' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__nqx_setup"
else
    echo 'problem'
    #if [ -f "/mnt/beegfs/softs/opt/core/mambaforge/22.11.1-4/etc/profile.d/conda.sh" ]; then
    #    . "/mnt/beegfs/softs/opt/core/mambaforge/22.11.1-4/etc/profile.d/conda.sh"
    #else
    #    export PATH="/mnt/beegfs/softs/opt/core/mambaforge/22.11.1-4/bin:$PATH"
    #fi
fi
unset __nqx_setup
"""


@app.command()
def init(
    permanent: Annotated[
        bool,
        typer.Option(
            help="Add the initialization block to the shell profile.",
        ),
    ] = False,
):
    """
    Install this tool in the shell.
    """

    nqx_exe = shutil.which("nqx")
    logging.debug("Found nqx installation at path: %s", nqx_exe)
    setup_block = setup_block_template.format(nqx_exe)

    if not permanent:
        print()
        print(
            "You must execute the following piece of code in your shell to activate nqx:"
        )
        print()
        nqx_exe = nqx_exe.replace(" ", r"\ ")
        print(f'eval "$({nqx_exe} hook)"')
        print()
    else:
        bashrc = Path.home() / ".bashrc"
        with open(bashrc) as f:
            bashrc_content = f.read()

        MAGIC_STRING = "# !! Contents within this block are managed by 'nqx init' !!"
        # check if the string 'Contents within this block are managed by 'conda init' is already there
        if MAGIC_STRING in bashrc_content:
            print("nqx initialization block already exists in ~/.bashrc")
            return 1

        with open(bashrc, "a") as f:
            f.write(">>> nqx initialize >>>")
            f.print(MAGIC_STRING)
            f.write(setup_block)
            f.write("<<< nqx initialize <<<")
        return 0
