import ipaddress

import click
from vmanage.api.device import Device
from vmanage.api.monitor_network import MonitorNetwork
from vmanage.cli.show.print_utils import print_json


@click.command()
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def peers(ctx, device, json):
    """
    Show OMP peer information
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    mn = MonitorNetwork(ctx.auth, ctx.host, ctx.port)

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
        print_json(omp_peers)
    else:
        for peer in omp_peers:
            click.echo(
                f"{peer['peer']:<16} {peer['type']:<7} {peer['domain-id']:<6} {'X':<7} {peer['site-id']:<6} {peer['state']:<8} {peer['up-time']:<16} X/X/X"
            )


@click.command()
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def received(ctx, device, json):
    """
    Show OMP peer information
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    mn = MonitorNetwork(ctx.auth, ctx.host, ctx.port)

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
        click.echo("VPN    PREFIX             PROTOCOL   FROM-PEER       Originator      COLOR           STATUS")
        click.echo("------------------------------------------------------------------------------------------------")
    # try:
    omp_peers = mn.get_omp_routes_received(system_ip)
    if json:
        print_json(omp_peers)
    else:
        for peer in omp_peers:
            click.echo(
                f"{peer['vpn-id']:<6} {peer['prefix']:<18} {peer['protocol']:<10} {peer['from-peer']:<15} {peer['originator']:<15} {peer['color']:<15} {peer['attribute-type']:<16}"
            )


@click.command()
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def advertised(ctx, device, json):
    """
    Show OMP peer information
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    mn = MonitorNetwork(ctx.auth, ctx.host, ctx.port)

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
        click.echo("VPN    PREFIX             PROTOCOL   ")
        click.echo("-------------------------------------")
    # try:
    omp_peers = mn.get_omp_routes_advertised(system_ip)
    if json:
        print_json(omp_peers)
    else:
        for peer in omp_peers:
            if 'protocol' in peer:
                protocol = peer['protocol']
            else:
                protocol = ''
            click.echo(f"{peer['vpn-id']:<6} {peer['prefix']:<18} {protocol:<10}")


@click.group()
def routes():
    """
    Show OMP information
    """


routes.add_command(received)
routes.add_command(advertised)


@click.group()
def omp():
    """
    Show OMP information
    """


omp.add_command(peers)
omp.add_command(routes)
