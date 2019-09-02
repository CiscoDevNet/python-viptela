import click
import pprint

@click.command()
@click.argument('type', default='all')
# @click.option('--output', '-o', help="output File name ")
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_context
def policy(ctx, type):
    """
    Show policy information
    """

    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)
    click.echo('Policies:')
    policy_lists = vmanage_session.get_policy_list_list()
    policy_definition_list = vmanage_session.get_policy_definition_list()
    pp.pprint(policy_lists)
    pp.pprint(policy_definition_list)
    
