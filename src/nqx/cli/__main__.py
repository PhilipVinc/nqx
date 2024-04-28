from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True)
state = {"verbose": False}


@app.command()
def create(username: str):
    print(f"Creating user: {username}")
    if state["verbose"]:
        print("Just created a user")


@app.command()
def delete(
    username: str,
    force: Annotated[
        bool,
        typer.Option(
            prompt="Are you sure you want to delete the user?",
            help="Force deletion without confirmation.",
        ),
    ],
):
    """
    Delete a user with USERNAME.

    If --force is not used, will ask for confirmation.
    """
    if force:
        print(f"Deleting user: {username}")
    else:
        print("Operation cancelled")
    if state["verbose"]:
        print("Just deleted a user")


@app.command()
def delete_all(
    force: Annotated[
        bool,
        typer.Option(
            prompt="Are you sure you want to delete ALL users?",
            help="Force deletion without confirmation.",
        ),
    ],
):
    """
    Delete ALL users in the database.

    If --force is not used, will ask for confirmation.
    """
    if force:
        print("Deleting all users")
    else:
        print("Operation cancelled")
    if state["verbose"]:
        print("Just deleted a user")


@app.callback()
def main(verbose: Annotated[bool, typer.Option(help="ciao")] = False):
    """
    Manage users in the awesome CLI app.
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


@app.command()
def init():
    print("Initializing user database")
