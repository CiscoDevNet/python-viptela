import click
from vmanage.api.utilities import Utilities


@click.command('serial-file')
@click.option('--file', '-f', 'input_file', help="Input file name", required=True)
@click.pass_obj
def serial_file(ctx, input_file):
    """
    Import serial file
    """
    vmanage_utilities = Utilities(ctx.auth, ctx.host, ctx.port)

    click.echo(f'Uploading serial file... {input_file}')
    result = vmanage_utilities.upload_file(input_file)
    click.echo(result)
