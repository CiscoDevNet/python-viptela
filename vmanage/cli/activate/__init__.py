import click
from vmanage.cli.activate.central_policy import central_policy


@click.group()
def activate():
    """
    Activate commands
    """


activate.add_command(central_policy)
