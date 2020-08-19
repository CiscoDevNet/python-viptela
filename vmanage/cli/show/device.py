import pprint
import ipaddress
import click
from vmanage.api.device import Device


@click.command()
@click.argument('dev', required=False)
@click.option('--type',
              '-t',
              'device_type',
              required=False,
              default='all',
              type=click.Choice(['edge', 'control', 'all']),
              help="Device type [vedges, controllers]")
@click.option('--json/--no-json', default=False)
@click.pass_obj
def status(ctx, dev, device_type, json):  #pylint: disable=unused-argument
    """
    Show device status information
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    # output = mn.get_control_connections_history(sysip)
    # vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if dev:
        # Check to see if we were passed in a device IP address or a device name
        try:
            system_ip = ipaddress.ip_address(dev)
            device_dict = vmanage_device.get_device_status(system_ip)
        except ValueError:
            device_dict = vmanage_device.get_device_status(dev, key='host-name')

        if device_dict:
            pp.pprint(device_dict)
        else:
            click.secho(f"Could not find device {dev}", err=True, fg='red')
    else:
        device_list = vmanage_device.get_device_status_list()
        if json:
            pp.pprint(device_list)
        else:
            click.echo(
                f"{'Hostname':20} {'System IP':15} {'Model':15} {'Site':6} {'Status':9} {'BFD':>3} {'OMP':>3} {'CON':>3} {'Version':8} {'UUID':40} {'Serial'}"
            )
            for device_entry in device_list:
                if 'bfdSessionsUp' in device_entry:
                    bfd = device_entry['bfdSessionsUp']
                else:
                    bfd = ''
                if 'ompPeers' in device_entry:
                    omp = device_entry['ompPeers']
                else:
                    omp = ''
                if 'controlConnections' in device_entry:
                    control = device_entry['controlConnections']
                else:
                    control = ''
                click.echo(
                    f"{device_entry['host-name']:20} {device_entry['system-ip']:15} {device_entry['device-model']:15} {device_entry['site-id']:6} {device_entry['reachability']:9} {bfd:>3} {omp:>3} {control:>3} {device_entry['version']:8} {device_entry['uuid']:40} {device_entry['board-serial']}"
                )

    #     device_list = [device_ip]


@click.command()
@click.argument('dev', required=False)
@click.option('--type',
              '-t',
              'device_type',
              required=False,
              default='all',
              type=click.Choice(['edge', 'control', 'all']),
              help="Device type [vedges, controllers]")
@click.option('--json/--no-json', default=False)
@click.pass_obj
def config(ctx, dev, device_type, json):
    """
    Show device config information
    """
    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    #pylint: disable=too-many-nested-blocks
    if dev:
        # Check to see if we were passed in a device IP address or a device name
        try:
            system_ip = ipaddress.ip_address(dev)
            device_dict = vmanage_device.get_device_status(system_ip)
        except ValueError:
            device_dict = vmanage_device.get_device_status(dev, key='host-name')

        if device_dict:
            if device_dict['device-type'] in ['vmanage', 'vbond', 'vsmart']:
                device_type = 'controllers'
            else:
                device_type = 'vedges'

            device_config = vmanage_device.get_device_config(device_type, device_dict['system-ip'])
            pp.pprint(device_config)
        else:
            click.secho(f"Could not find device {dev}", err=True, fg='red')

    else:
        if not json:
            click.echo(
                f"{'Hostname':20} {'Device IP':15} {'Model':15} {'Site':6} {'State':9} {'Template':16} {'Status':7} {'Connection':10} {'Version':7}"
            )
        if device_type in ['all', 'control']:
            device_list = vmanage_device.get_device_config_list('controllers')

            if json:
                pp.pprint(device_list)
            else:
                for device_entry in device_list:
                    if 'template' in device_entry:
                        template = device_entry['template']
                    else:
                        template = ''

                    device_name = device_entry['host-name'] if 'host-name' in device_entry else 'Unknown'
                    reachability = device_entry['reachability'] if 'reachability' in device_entry else 'Unknown'
                    site_id = device_entry['site-id'] if 'site-id' in device_entry else 'Unknown'
                    config_status_message = device_entry[
                        'configStatusMessage'] if 'configStatusMessage' in device_entry else 'Unknown'
                    vmanage_connection_state = device_entry[
                        'vmanageConnectionState'] if 'vmanageConnectionState' in device_entry else 'Unknown'
                    version = device_entry['version'] if 'version' in device_entry else 'Unknown'
                    click.echo(
                        f"{device_name:20} {device_entry['deviceIP']:15} {device_entry['deviceModel']:15} {site_id:6} {reachability:9} {template:16} {config_status_message:7} {vmanage_connection_state:10} {version:7}"
                    )

        if device_type in ['all', 'edge']:
            device_list = vmanage_device.get_device_config_list('vedges')
            if json:
                pp.pprint(device_list)
            else:
                for device_entry in device_list:
                    if 'host-name' in device_entry:
                        if 'template' in device_entry:
                            template = device_entry['template']
                        else:
                            template = ''
                        device_name = device_entry['host-name'] if 'host-name' in device_entry else 'Unknown'
                        reachability = device_entry['reachability'] if 'reachability' in device_entry else 'Unknown'
                        site_id = device_entry['site-id'] if 'site-id' in device_entry else 'Unknown'
                        config_status_message = device_entry[
                            'configStatusMessage'] if 'configStatusMessage' in device_entry else 'Unknown'
                        vmanage_connection_state = device_entry[
                            'vmanageConnectionState'] if 'vmanageConnectionState' in device_entry else 'Unknown'
                        version = device_entry['version'] if 'version' in device_entry else 'Unknown'
                        click.echo(
                            f"{device_name:20} {device_entry['deviceIP']:15} {device_entry['deviceModel']:15} {site_id:6} {reachability:9} {template:16} {config_status_message:7} {vmanage_connection_state:10} {version:7}"
                        )


@click.group()
def device():
    """
    Show device information
    """


device.add_command(status)
device.add_command(config)
