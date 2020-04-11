import click
import pprint
import ipaddress

@click.command()
@click.argument('device', required=True)
@click.option('--json/--no-json', default=False)
@click.pass_context
def list(ctx, device, json):
    """
    Show Interfaces
    """
    vmanage_session = ctx.obj

    if device:
        # Check to see if we were passed in a device IP address or a device name
        try:
            ip = ipaddress.ip_address(device)
            system_ip = device
        except ValueError:
            device_dict = vmanage_session.get_device_status(device, key='host-name')
            if 'system-ip' in device_dict:
                system_ip = device_dict['system-ip']
        device_list = [system_ip]

    if not json:
        click.echo("IFNAME           VPNID                  IP ADDR             MAC ADDR       OPER STATE                DESC")
        click.echo("----------------------------------------------------------------------------------------------------------------------")

    for device in device_list:
        try:
            interfaces = vmanage_session.get_device_data('interface', device)
            for interface in interfaces:
                if json:
                    pp = pprint.PrettyPrinter(indent=2)
                    pp.pprint(interface)
                else:
                    if 'hwaddr' not in interface:
                        interface['hwaddr'] = ''
                    if 'desc' not in interface:
                        interface['desc'] = ''
                    click.echo(f"{interface['ifname']:17} {interface['vpn-id']:17} {interface['ip-address']:17} {interface['hwaddr']:25} {interface['if-oper-status']:17} {interface['desc']:17}")
        except:
            pass
    pass

@click.group()
@click.pass_context
def interface(ctx):
    """
    Show real-time information
    """

interface.add_command(list)
