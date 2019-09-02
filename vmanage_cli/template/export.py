    
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

    click.echo(f'Exporting templates to {file}')
    feature_template_list = vmanage_session.get_feature_template_list()
    device_template_list = vmanage_session.get_device_template_list()
    
    template_export = {
        'feature_templates': feature_template_list,
        'device_templates': device_template_list
    }

    with open(file, 'w') as f:
        json.dump(template_export, f, indent=4, sort_keys=True)