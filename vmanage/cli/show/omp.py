import ipaddress
import pprint

import click
from vmanage.api.device import Device
from vmanage.api.monitor_network import MonitorNetwork


@click.command()
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def peers(ctx, device, json):
    """
    Show OMP peer information
    """

    vmanage_device = Device(ctx.auth, ctx.host)
    mn = MonitorNetwork(ctx.auth, ctx.host)

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
        click.echo("                         DOMAIN OVERLAY SITE")
        click.echo("PEER             TYPE    ID     ID      ID     STATE    UPTIME           R/I/S")
        click.echo("---------------------------------------------------------------------------------------")
    # try:
    omp_peers = mn.get_omp_peers(system_ip)
    if json:
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(omp_peers)
    else:
        for peer in omp_peers:
            click.echo(
                f"{peer['peer']:<16} {peer['type']:<7} {peer['domain-id']:<6} {'X':<7} {peer['site-id']:<6} {peer['state']:<8} {peer['up-time']:<16} X/X/X"
            )
    # except:
    #    pass


@click.group()
def omp():
    """
    Show OMP information
    """


omp.add_command(peers)
