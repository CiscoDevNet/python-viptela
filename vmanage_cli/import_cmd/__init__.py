import click
from .templates import templates
from .policy import policy

@click.group('import')
@click.pass_context
def import_cmd(ctx):
    """
    Import commands
    """

import_cmd.add_command(templates)
import_cmd.add_command(policy)