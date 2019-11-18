import click
from vmanage.cli.show.device import device
from vmanage.cli.show.templates import templates
from vmanage.cli.show.policies import policies
from vmanage.cli.show.omp import omp
from vmanage.cli.show.control import control

@click.group()
@click.pass_context
def show(ctx):
    """
    Show commands
    """

show.add_command(device)
show.add_command(templates)
show.add_command(policies)
show.add_command(omp)
show.add_command(control)