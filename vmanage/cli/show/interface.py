import ipaddress

import click
from vmanage.api.device import Device
from vmanage.cli.show.print_utils import print_json


@click.command(name='list')
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def list_interface(ctx, device, json):
    """
    Show Interfaces
    """
    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)

    if device:
        # Check to see if we were passed in a device IP address or a device name
        try:
            ipaddress.ip_address(device)
            system_ip = device
        except ValueError:
            device_dict = vmanage_device.get_device_status(device, key='host-name')
            if 'system-ip' in device_dict:
                system_ip = device_dict['system-ip']
        device_list = [system_ip]

    if not json:
        click.echo("IFNAME            VPNID  IP ADDR          MAC ADDR                  OPER STATE            DESC")
        click.echo("-" * 118)

    for dev in device_list:
        interfaces = vmanage_device.get_device_data('interface', dev)
        for iface in interfaces:
            if json:
                print_json(iface)
            else:
                if 'hwaddr' not in iface:
                    iface['hwaddr'] = ''
                if 'desc' not in iface:
                    iface['desc'] = ''
                if 'ip-address' not in iface:
                    iface['ip-address'] = ''
                click.echo(
                    f"{iface['ifname']:17} {iface['vpn-id']:6} {iface['ip-address']:16} {iface['hwaddr']:25} {iface['if-oper-status']:17} {iface['desc']:17}"
                )


@click.group()
def interface():
    """
    Show real-time information
    """


interface.add_command(list_interface)
