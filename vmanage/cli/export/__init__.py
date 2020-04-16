import click
from vmanage.cli.export.templates import templates
from vmanage.cli.export.policies import policies
from vmanage.cli.export.attachments import attachments


@click.group()
def export():
    """
    Export commands
    """


export.add_command(templates)
export.add_command(policies)
export.add_command(attachments)
