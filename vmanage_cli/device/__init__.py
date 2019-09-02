import click
from .show import show

@click.group()
@click.pass_context
def device(ctx):
    """
    Device related commands
    """
    print("poop")

device.add_command(show)