import click
from vmanage.cli.export.templates import templates
from vmanage.cli.export.policies import policies

@click.group()
@click.pass_context
def export(ctx):
    """
    Export commands
    """

export.add_command(templates)
export.add_command(policies)