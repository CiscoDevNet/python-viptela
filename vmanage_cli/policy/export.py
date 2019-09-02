    
import click
import json
from cisco_sdwan import vmanage

@click.command()
@click.argument('type', default='all')
@click.option('--file', '-f', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
def export(ctx, type, file):
    """
    Show device information
    """

    vmanage_session = vmanage.vmanage_session(host=ctx.obj.host, user=ctx.obj.user, password=ctx.obj.password)

    click.echo(f'Exporting policy to {file}')
    policy_lists = vmanage_session.get_policy_list_list()

    export = {
        'policy_lists': policy_lists
    }

    with open(file, 'w') as f:
        json.dump(export, f, indent=4, sort_keys=True)