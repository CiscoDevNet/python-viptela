import click
from vmanage.cli.activate.central_policy import central_policy


@click.group()
@click.pass_context
def activate(ctx):
    """
    Show commands
    """


activate.add_command(central_policy)
