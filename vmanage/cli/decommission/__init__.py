import click
from vmanage.cli.decommission.device import device


@click.group()
def decommission():
    """
    Decommission commands
    """


decommission.add_command(device)
