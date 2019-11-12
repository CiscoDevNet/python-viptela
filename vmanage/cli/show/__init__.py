import click
from vmanage.cli.show.device import device
from vmanage.cli.show.template import template
from vmanage.cli.show.policy import policy
from vmanage.cli.show.omp import omp
from vmanage.cli.show.control import control

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