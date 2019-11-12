import click
from vmanage.command.show.device import device
from vmanage.command.show.template import template
from vmanage.command.show.policy import policy
from vmanage.command.show.omp import omp
from vmanage.command.show.control import control

@click.group()
@click.pass_context
def show(ctx):
    """
    Show commands
    """

show.add_command(device)
show.add_command(template)
show.add_command(policy)
show.add_command(omp)
show.add_command(control)