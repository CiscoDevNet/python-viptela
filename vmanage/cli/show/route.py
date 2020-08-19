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
    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)

    # Check to see if we were passed in a device IP address or a device name
    try:
        ip = ipaddress.ip_address(device)
        system_ip = ip
    except ValueError:
        device_dict = vmanage_device.get_device_status(device, key='host-name')
        if 'system-ip' in device_dict:
            system_ip = device_dict['system-ip']
        else:
            system_ip = None

    if not json:
        click.echo("VPNID  PREFIX               NEXT HOP              PROTOCOL      ")
        click.echo("----------------------------------------------------------------")

    routes = vmanage_device.get_device_data('ip/routetable', system_ip)
    for rte in routes:
        if json:
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(rte)
        else:
            if 'nexthop-addr' not in rte:
                rte['nexthop-addr'] = ''
            click.echo(f"{rte['vpn-id']:5}  {rte['prefix']:<20} {rte['nexthop-addr']:<20}  {rte['protocol']:8}")


@click.group()
def route():
    """
    Show device route information
    """


route.add_command(table)
