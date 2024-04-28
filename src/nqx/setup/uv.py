import os
from ..utils import execute


def is_installed():
    return os.path.exists("$HOME/.cargo/bin/uv")


def install(verbose=False):
    execute("curl -LsSf https://astral.sh/uv/install.sh | sh")
