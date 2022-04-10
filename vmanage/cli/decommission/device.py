import click
from vmanage.api.device import Device


@click.command('device')
@click.argument('device_name', required=True)
@click.pass_obj
def device(ctx, device_name):
    """
    Decommission device
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    status = vmanage_device.get_device_status(device_name, key='host-name')
    if 'uuid' in status:
        vmanage_device.put_device_decommission(status['uuid'])
    else:
        click.secho(f'Cannot find UUID for device {device}', fg="red")
