import click
import pprint


@click.command()
@click.option('--device_ip', default='', help="Show information for device")
@click.option('--json/--no-json', default=False)
@click.option('--type', default='all',
               help="Device type [vedges, controllers]",
               type=click.Choice(['vedges', 'controllers', 'all']))
@click.pass_context
def devices(ctx, device_ip, type, json):
    """
    Show device information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)
    if len(device_ip) > 0:
        device = vmanage_session.get_device_by_device_ip(device_ip)
        if device:
            pp.pprint(device)
    else:
        click.echo(f"{'Hostname':20} {'Device IP':15} {'Model':12} {'State':9} {'Site':4} {'Template':16} {'Status':7} {'Connection':10} {'Version':7}")
        if type in ['all', 'control']:
            device_list = vmanage_session.get_device_list('controllers')
            for device in device_list:
                if 'template' in device:
                    template = device['template']
                else:
                    template = ''
                if json:
                    pp.pprint(device)
                else:
                    click.echo(f"{device['host-name']:20} {device['deviceIP']:15} {device['deviceModel']:12} {device['reachability']:9} {device['site-id']:4} {template:16} {device['configStatusMessage']:7} {device['vmanageConnectionState']:10} {device['version']:7}")

        if type in ['all', 'edge']:
            device_list = vmanage_session.get_device_list('vedges')
            for device in device_list:
                if 'host-name' in device:
                    if 'template' in device:
                        template = device['template']
                    else:
                        template = ''
                    click.echo(f"{device['host-name']:20} {device['deviceIP']:15} {device['deviceModel']:12} {device['reachability']:9} {device['site-id']:4} {template:16} {device['configStatusMessage']:7} {device['vmanageConnectionState']:10} {device['version']:7}")