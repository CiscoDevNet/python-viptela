import click
from vmanage.cli.deactivate.central_policy import central_policy

@click.group()
@click.pass_context
def deactivate(ctx):
    """
    Show commands
    """

deactivate.add_command(central_policy)