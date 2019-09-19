import click
from .device import device
from .templates import templates
from .policy import policy
from .omp import omp
from .control import control

@click.group()
@click.pass_context
def show(ctx):
    """
    Show commands
    """

show.add_command(device)
show.add_command(templates)
show.add_command(policy)
show.add_command(omp)
show.add_command(control)