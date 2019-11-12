    
import click
import json

@click.command()
@click.argument('type', default='all')
@click.option('--file', '-f', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_context
def policy(ctx, type, file):
    """
    Export policy to file
    """

    vmanage_session = ctx.obj
    click.echo(f'Exporting policy to {file}')
    vmanage_session.export_policy_to_file(file)