import click
from vmanage.api.device import Device


@click.command()
@click.option('--ip', 'ip', help="IP address of the device", required=True)
@click.option('--vpn', 'vpn', help="VPN ID", required=True)
@click.option('--name', 'name', help="Interface name", required=True)
@click.pass_obj
def interface(ctx, ip, vpn, name):
    """
    Reset interface
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    vmanage_device.post_reset_interface(ip, vpn, name)
