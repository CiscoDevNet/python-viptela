import click
from vmanage.cli.import_cmd.templates import templates
from vmanage.cli.import_cmd.policies import policies


@click.group('import')
def import_cmd():
    """
    Import commands
    """


import_cmd.add_command(templates)
import_cmd.add_command(policies)
