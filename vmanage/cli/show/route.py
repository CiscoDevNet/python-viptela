import ipaddress
import pprint

import click
from vmanage.api.device import Device


@click.command()
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def table(ctx, device, json):
    """
    Show Interfaces
    """
    vmanage_device = Device(ctx.auth, ctx.host)

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
        click.echo("VPNID           PREFIX                  NEXT HOP                 MAC ADDR       OPER STATE")
        click.echo("---------------------------------------------------------------------------------------------")

    for dev in device_list:
        routes = vmanage_device.get_device_data('ip/routetable', dev)
        for rte in routes:
            if json:
                pp = pprint.PrettyPrinter(indent=2)
                pp.pprint(rte)
            else:
                if 'nexthop-addr' not in rte:
                    rte['nexthop-addr'] = ''
                click.echo(f"{rte['vpn-id']:5} {rte['prefix']:40} {rte['nexthop-addr']:1} {rte['protocol']}")


@click.group()
def route():
    """
    Show device route information
    """


route.add_command(table)
