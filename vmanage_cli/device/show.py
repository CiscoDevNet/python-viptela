    
import click
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

    if type in ['all', 'control']:
        click.echo('Controllers:')
        device_list = vmanage_session.get_device_list('controllers')
        for device in device_list:
            if 'template' in device:
                template = device['template']
            else:
                template = ''
            click.echo(f"{device['host-name']:16} {device['personality']:7} {device['site-id']:4} {device['deviceIP']:15} {template:16} {device['configStatusMessage']}")
        click.echo('')

    if type in ['all', 'edge']:
        click.echo('Edges:')
        device_list = vmanage_session.get_device_list('vedges')
        for device in device_list:
            if 'host-name' in device:
                if 'template' in device:
                    template = device['template']
                else:
                    template = ''
                click.echo(f"{device['host-name']:16} {device['personality']:7} {device['site-id']:4} {device['deviceIP']:15} {template:16} {device['configStatusMessage']}")