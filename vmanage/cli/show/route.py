import click
import pprint
import ipaddress
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
            ip = ipaddress.ip_address(device)
            system_ip = device
        except ValueError:
            device_dict = vmanage_device.get_device_status(device, key='host-name')
            if 'system-ip' in device_dict:
                system_ip = device_dict['system-ip']
        device_list = [system_ip]

    if not json:
        click.echo("VPNID           PREFIX                  NEXT HOP                 MAC ADDR       OPER STATE")
        click.echo("---------------------------------------------------------------------------------------------")

    for device in device_list:
        routes = vmanage_device.get_device_data('ip/routetable', device)
        for route in routes:
            if json:
                pp = pprint.PrettyPrinter(indent=2)
                pp.pprint(route)
            else:
                if 'nexthop-addr' not in route:
                    route['nexthop-addr'] = ''
                click.echo(f"{route['vpn-id']:5} {route['prefix']:40} {route['nexthop-addr']:1} {route['protocol']}")

@click.group()
@click.pass_context
def route(ctx):
    """
    Show device route information
    """

route.add_command(table)
