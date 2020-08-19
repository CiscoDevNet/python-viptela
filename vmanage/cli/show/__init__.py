import click
from vmanage.cli.show.device import device
from vmanage.cli.show.templates import templates
from vmanage.cli.show.policies import policies
from vmanage.cli.show.omp import omp
from vmanage.cli.show.control import control
from vmanage.cli.show.interface import interface
from vmanage.cli.show.route import route
from vmanage.cli.show.org import org
from vmanage.cli.show.vbond import vbond
from vmanage.cli.show.ca_type import ca_type
from vmanage.cli.show.root_cert import root_cert


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
show.add_command(org)
show.add_command(vbond)
show.add_command(ca_type)
show.add_command(root_cert)
