import click
from vmanage.cli.show.device import device
from vmanage.cli.show.templates import templates
from vmanage.cli.show.policies import policies
from vmanage.cli.show.omp import omp
from vmanage.cli.show.control import control
from vmanage.cli.show.interface import interface
from vmanage.cli.show.route import route


@click.group()
def show():
    """
    Show commands
    """


show.add_command(device)
show.add_command(templates)
show.add_command(policies)
show.add_command(omp)
show.add_command(control)
show.add_command(interface)
show.add_command(route)
