    
import click
import json

@click.command()
@click.argument('type', default='all')
@click.option('--file', '-f', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_context
def policies(ctx, type, file):
    """
    Export policies to file
    """

    vmanage_session = ctx.obj
    click.echo(f'Exporting policies to {file}')
    vmanage_session.export_policy_to_file(file)