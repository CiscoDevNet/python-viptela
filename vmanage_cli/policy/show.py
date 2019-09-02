import click
import pprint
from cisco_sdwan import vmanage

@click.command()
@click.argument('type', default='all')
# @click.option('--output', '-o', help="output File name ")
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_context
def show(ctx, type):
    """
    Show device information
    """

    vmanage_session = vmanage.vmanage_session(host=ctx.obj.host, user=ctx.obj.user, password=ctx.obj.password)
    pp = pprint.PrettyPrinter(indent=2)
    click.echo('Policies:')
    policy_lists = vmanage_session.get_policy_list_list()

    pp.pprint(policy_lists)
    
