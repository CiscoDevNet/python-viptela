import pprint

import click
from vmanage.api.device import Device


@click.command()
@click.argument('device', required=False)
@click.option('--type',
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

    vmanage_device = Device(ctx.auth, ctx.host)
    # output = mn.get_control_connections_history(sysip)
    # vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if dev:
        # Check to see if we were passed in a device IP address or a device name
        try:
            device_dict = vmanage_device.get_device_status(dev)
        except ValueError:
            device_dict = vmanage_device.get_device_status(dev, key='host-name')
        pp.pprint(device_dict)
    else:
        device_list = vmanage_device.get_device_status_list()
        if json:
            pp.pprint(device_list)
        else:
            click.echo(
                f"{'Hostname':20} {'System IP':15} {'Model':15} {'Site':6} {'Status':9} {'BFD':>3} {'OMP':>3} {'CON':>3} {'Version':8} {'UUID':40} {'Serial'}"
            )
            for dv in device_list:
                if 'bfdSessionsUp' in dv:
                    bfd = dv['bfdSessionsUp']
                else:
                    bfd = ''
                if 'ompPeers' in dv:
                    omp = dv['ompPeers']
                else:
                    omp = ''
                if 'controlConnections' in dv:
                    control = dv['controlConnections']
                else:
                    control = ''
                click.echo(
                    f"{dv['host-name']:20} {dv['system-ip']:15} {dv['device-model']:15} {dv['site-id']:6} {dv['reachability']:9} {bfd:>3} {omp:>3} {control:>3} {dv['version']:8} {dv['uuid']:40} {dv['board-serial']}"
                )

    #     device_list = [device_ip]


@click.command()
@click.argument('device', required=False)
@click.option('--type',
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
    vmanage_device = Device(ctx.auth, ctx.host)
    pp = pprint.PrettyPrinter(indent=2)

    #pylint: disable=too-many-nested-blocks
    if dev:
        # Check to see if we were passed in a device IP address or a device name
        try:
            device_dict = vmanage_device.get_device_status(dev)
        except ValueError:
            device_dict = vmanage_device.get_device_status(dev, key='host-name')

        if device_dict['device-type'] in ['vmanage', 'vbond', 'vsmart']:
            device_type = 'controllers'
        else:
            device_type = 'vedges'

        device_config = vmanage_device.get_device_config(device_type, device_dict['system-ip'])
        pp.pprint(device_config)

    else:
        click.echo(
            f"{'Hostname':20} {'Device IP':15} {'Model':15} {'Site':6} {'State':9} {'Template':16} {'Status':7} {'Connection':10} {'Version':7}"
        )
        if device_type in ['all', 'control']:
            device_list = vmanage_device.get_device_config_list('controllers')

            if json:
                pp.pprint(device_list)
            else:
                for dv in device_list:
                    if 'template' in dev:
                        template = dev['template']
                    else:
                        template = ''

                    device_name = dv['host-name'] if 'host-name' in dv else 'Unknown'
                    reachability = dv['reachability'] if 'reachability' in dv else 'Unknown'
                    site_id = dv['site-id'] if 'site-id' in dv else 'Unknown'
                    config_status_message = dv['configStatusMessage'] if 'configStatusMessage' in dv else 'Unknown'
                    vmanage_connection_state = dv[
                        'vmanageConnectionState'] if 'vmanageConnectionState' in dv else 'Unknown'
                    version = dv['version'] if 'version' in dv else 'Unknown'
                    click.echo(
                        f"{device_name:20} {dv['deviceIP']:15} {dv['deviceModel']:15} {site_id:6} {reachability:9} {template:16} {config_status_message:7} {vmanage_connection_state:10} {version:7}"
                    )

        if type in ['all', 'edge']:
            device_list = vmanage_device.get_device_config_list('vedges')
            if json:
                pp.pprint(device_list)
            else:
                for dv in device_list:
                    if 'host-name' in dv:
                        if 'template' in dv:
                            template = dv['template']
                        else:
                            template = ''
                        device_name = dv['host-name'] if 'host-name' in dv else 'Unknown'
                        reachability = dv['reachability'] if 'reachability' in dv else 'Unknown'
                        site_id = dv['site-id'] if 'site-id' in dv else 'Unknown'
                        config_status_message = dv['configStatusMessage'] if 'configStatusMessage' in dv else 'Unknown'
                        vmanage_connection_state = dv[
                            'vmanageConnectionState'] if 'vmanageConnectionState' in dv else 'Unknown'
                        version = dv['version'] if 'version' in dv else 'Unknown'
                        click.echo(
                            f"{device_name:20} {dv['deviceIP']:15} {dv['deviceModel']:15} {site_id:6} {reachability:9} {template:16} {config_status_message:7} {vmanage_connection_state:10} {version:7}"
                        )


@click.group()
def device():
    """
    Show device information
    """


device.add_command(status)
device.add_command(config)
