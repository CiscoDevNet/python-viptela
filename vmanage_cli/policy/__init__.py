import click
from .show import show
from .export import export

@click.group()
@click.pass_context
def policy(ctx):
    """
    Policy related commands
    """
    pass

policy.add_command(show)
policy.add_command(export)