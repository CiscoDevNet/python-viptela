import click
import pprint
import ipaddress


@click.command()
@click.argument('device', required=False)
@click.option('--type', required=False, default='all',
                type=click.Choice(['edge', 'control', 'all']),
                help="Device type [vedges, controllers]")
@click.option('--json/--no-json', default=False)
@click.pass_context
def status(ctx, device, type, json):
    """
    Show device status information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if device:
        # Check to see if we were passed in a device IP address or a device name
        try:
            ip = ipaddress.ip_address(device)
            device_dict = vmanage_session.get_device_status(device)
        except ValueError:
            device_dict = vmanage_session.get_device_status(device, key='host-name')
            if 'system-ip' in device_dict:
                system_ip = device_dict['system-ip'] 
        pp.pprint(device_dict)
    else:
        device_list = vmanage_session.get_device_status_list()
        if json:
            pp.pprint(device_list)
        else:
            click.echo(f"{'Hostname':20} {'System IP':15} {'Model':15} {'Site':6} {'Status':9} {'BFD':>3} {'OMP':>3} {'CON':>3} {'Version':8} {'UUID':40} {'Serial'}")
            for device in device_list:
                if 'bfdSessionsUp' in device:
                    bfd = device['bfdSessionsUp']
                else:
                    bfd = ''
                if 'ompPeers' in device:
                    omp = device['ompPeers']
                else:
                    omp = ''    
                if 'controlConnections' in device:
                    control = device['controlConnections']
                else:
                    control = ''    
                click.echo(f"{device['host-name']:20} {device['system-ip']:15} {device['device-model']:15} {device['site-id']:6} {device['reachability']:9} {bfd:>3} {omp:>3} {control:>3} {device['version']:8} {device['uuid']:40} {device['board-serial']}")

    #     device_list = [device_ip]

@click.command()
@click.argument('device', required=False)
@click.option('--type', required=False, default='all',
                type=click.Choice(['edge', 'control', 'all']),
                help="Device type [vedges, controllers]")
@click.option('--json/--no-json', default=False)
@click.pass_context
def config(ctx, device, type, json):
    """
    Show device config information
    """    
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if device:
        # Check to see if we were passed in a device IP address or a device name
        try:
            ip = ipaddress.ip_address(device)
            device_dict = vmanage_session.get_device_status(device)
        except ValueError:
            device_dict = vmanage_session.get_device_status(device, key='host-name')

        if device_dict['device-type'] in ['vmanage', 'vbond', 'vsmart']:
            type = 'controllers'
        else:
            type = 'vedges'

        device_config = vmanage_session.get_device_config(type, device_dict['system-ip'])
        pp.pprint(device_config)

    else:
        click.echo(f"{'Hostname':20} {'Device IP':15} {'Model':15} {'Site':6} {'State':9} {'Template':16} {'Status':7} {'Connection':10} {'Version':7}")
        if type in ['all', 'control']:
            device_list = vmanage_session.get_device_config_list('controllers')
            
            if json:
                pp.pprint(device_list)
            else:
                for device in device_list:
                    if 'template' in device:
                        template = device['template']
                    else:
                        template = ''

                    device_name = device['host-name'] if 'host-name' in device else 'Unknown'
                    reachability = device['reachability'] if 'reachability' in device else 'Unknown'
                    site_id = device['site-id'] if 'site-id' in device else 'Unknown'
                    config_status_message = device['configStatusMessage'] if 'configStatusMessage' in device else 'Unknown'
                    vmanage_connection_state = device['vmanageConnectionState'] if 'vmanageConnectionState' in device else 'Unknown'
                    version = device['version'] if 'version' in device else 'Unknown'
                    click.echo(f"{device_name:20} {device['deviceIP']:15} {device['deviceModel']:15} {site_id:6} {reachability:9} {template:16} {config_status_message:7} {vmanage_connection_state:10} {version:7}")

        if type in ['all', 'edge']:
            device_list = vmanage_session.get_device_config_list('vedges')
            if json:
                pp.pprint(device_list)
            else:            
                for device in device_list:
                    if 'host-name' in device:
                        if 'template' in device:
                            template = device['template']
                        else:
                            template = ''
                        device_name = device['host-name'] if 'host-name' in device else 'Unknown'
                        reachability = device['reachability'] if 'reachability' in device else 'Unknown'
                        site_id = device['site-id'] if 'site-id' in device else 'Unknown'
                        config_status_message = device['configStatusMessage'] if 'configStatusMessage' in device else 'Unknown'
                        vmanage_connection_state = device['vmanageConnectionState'] if 'vmanageConnectionState' in device else 'Unknown'
                        version = device['version'] if 'version' in device else 'Unknown'
                        click.echo(f"{device_name:20} {device['deviceIP']:15} {device['deviceModel']:15} {site_id:6} {reachability:9} {template:16} {config_status_message:7} {vmanage_connection_state:10} {version:7}")
@click.group()
@click.pass_context
def device(ctx):
    """
    Show device information
    """

device.add_command(status)
device.add_command(config)

