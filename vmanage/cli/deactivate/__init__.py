import click
from vmanage.cli.deactivate.central_policy import central_policy


@click.group()
def deactivate():
    """
    Deactivate commands
    """


deactivate.add_command(central_policy)
