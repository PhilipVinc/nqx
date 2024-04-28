import typer

from .app import app
from . import create
from . import list
from . import activate


def main():
    app()


if __name__ == "__main__":
    main()
