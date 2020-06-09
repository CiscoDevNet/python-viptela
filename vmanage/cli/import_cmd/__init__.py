import click
from vmanage.cli.import_cmd.templates import templates
from vmanage.cli.import_cmd.policies import policies
from vmanage.cli.import_cmd.attachments import attachments
from vmanage.cli.import_cmd.serial_file import serial_file
from vmanage.cli.import_cmd.root_cert import root_cert


@click.group('import')
def import_cmd():
    """
    Import commands
    """


import_cmd.add_command(templates)
import_cmd.add_command(policies)
import_cmd.add_command(attachments)
import_cmd.add_command(serial_file)
import_cmd.add_command(root_cert)
