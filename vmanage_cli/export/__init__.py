import click
from .templates import templates
from .policy import policy

@click.group()
@click.pass_context
def export(ctx):
    """
    Export commands
    """

export.add_command(templates)
export.add_command(policy)