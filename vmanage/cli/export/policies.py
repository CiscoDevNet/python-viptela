    
import click
import json
from vmanage.api.files import Files

@click.command()
@click.argument('type', default='all')
@click.option('--file', '-f', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_obj
def policies(ctx, type, file):
    """
    Export policies to file
    """

    vmanage_files = Files(ctx.auth, ctx.host)
    click.echo(f'Exporting policies to {file}')
    vmanage_files.export_policy_to_file(file)