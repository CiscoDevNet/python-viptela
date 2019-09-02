import click
from .show import show
from .export import export

@click.group()
@click.pass_context
def template(ctx):
    """
    Template related commands
    """
    pass

template.add_command(show)
template.add_command(export)