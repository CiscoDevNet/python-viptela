import ipaddress

import click
from vmanage.api.device import Device
from vmanage.api.monitor_network import MonitorNetwork
from vmanage.cli.show.print_utils import print_json


@click.command()
@click.argument('device', default=None, required=False)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def connections(ctx, device, json):
    """
    Show control connections
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    mn = MonitorNetwork(ctx.auth, ctx.host, ctx.port)

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
    else:
        control_device_dict = vmanage_device.get_device_config_dict(device_type='controllers', key_name='deviceIP')
        device_list = list(control_device_dict.keys())

    if not json:
        click.echo("LOCAL           PEER    PEER PEER            SITE   DOMAIN PEER            PEER            ")
        click.echo(
            "SYSTEM IP       TYPE    PROT SYSTEM IP       ID     ID     PRIVATE IP      PUBLIC IP       LOCAL COLOR      PROXY STATE UPTIME"
        )
        click.echo("-" * 115)

    for dev in device_list:
        try:
            control_connections = mn.get_control_connections(dev)
            if json:
                print_json(control_connections)
            else:
                for connection in control_connections:
                    click.echo(
                        f"{dev:15} {connection['peer-type']:7} {connection['protocol']:4} {connection['system-ip']:15} {connection['site-id']:6} {connection['domain-id']:6} {connection['private-ip']:15} {connection['public-ip']:15} {connection['local-color']:15}  {connection['state']:11} {connection['uptime']:11}"
                    )
        # TODO: figure out correct exception type to catch
        except Exception:
            pass


@click.command('connections-history')
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def connections_history(ctx, device, json):
    """
    Show control connections history
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    mn = MonitorNetwork(ctx.auth, ctx.host, ctx.port)

    # Check to see if we were passed in a device IP address or a device name
    try:
        ipaddress.ip_address(device)
        system_ip = device
    except ValueError:
        device_dict = vmanage_device.get_device_status(device, key='host-name')
        if 'system-ip' in device_dict:
            system_ip = device_dict['system-ip']

    if not json:
        click.echo(
            "PEER     PEER     PEER             SITE  DOMAIN PEER             PRIVATE PEER             PUBLIC                              LOCAL   REMOTE"
        )
        click.echo(
            "TYPE     PROTOCOL SYSTEM IP        ID    ID     PRIVATE IP       PORT    PUBLIC IP        PORT   LOCAL COLOR      STATE       ERROR   ERROR"
        )
        click.echo("-" * 139)
    try:
        control_connections_history = mn.get_control_connections_history(system_ip)
        if json:
            print_json(control_connections_history)
        else:
            for connection in control_connections_history:
                click.echo(
                    f"{connection['peer-type']:8} {connection['protocol']:8} {connection['system-ip']:16} {connection['site-id']:5} {connection['domain-id']:6} {connection['private-ip']:15} {connection['private-port']:8} {connection['private-ip']:15} {connection['private-port']:7} {connection['local-color']:15}  {connection['state']:11} {connection['local_enum']:7} {connection['local_enum-desc']}"
                )
    except Exception:
        pass


@click.group()
def control():
    """
    Show control information
    """


control.add_command(connections)
control.add_command(connections_history)
