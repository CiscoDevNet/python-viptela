    
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

    click.echo('Device Templates:')
    feature_template_list = vmanage_session.get_feature_template_list()
    for template in feature_template_list:
        click.echo(f"{template['templateName']:20} {template['templateDescription']:7}")
    # device_template_list = vmanage_session.get_device_template_list()
    # if feature_template_list:
    #     pp.pprint(feature_template_list)
    
