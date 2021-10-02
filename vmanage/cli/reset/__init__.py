import click
from vmanage.cli.reset.interface import interface


@click.group('reset')
def reset():
    """
    Reset commands
    """


reset.add_command(interface)
