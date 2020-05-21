import click
from vmanage.cli.set_cmd.org import org
from vmanage.cli.set_cmd.vbond import vbond
from vmanage.cli.set_cmd.ca_type import ca_type


@click.group('set')
def set_cmd():
    """
    vManage Settings set commands
    """


set_cmd.add_command(org)
set_cmd.add_command(vbond)
set_cmd.add_command(ca_type)
