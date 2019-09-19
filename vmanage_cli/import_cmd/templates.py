    
import click
import json
from cisco_sdwan import vmanage

@click.command()
@click.argument('type', default='all')
@click.option('--check/--no-check', default=False)
@click.option('--file', '-f', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_context
def templates(ctx, type, file, check):
    """
    Import templates from file
    """
    vmanage_session = ctx.obj
    click.echo(f'Importing templates from {file}')
    result = vmanage_session.import_templates_from_file(file, check_mode=check)
    print(f"Feature Template Updates: {result['feature_template_updates']}")
    print(f"Device Template Updates: {result['device_template_updates']}")