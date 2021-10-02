import click
from vmanage.api.device import Device


@click.command('device')
@click.argument('device', required=True)
@click.pass_obj
def device(ctx, decommdevice):
    """
    Decommission device
    """

    vmanage_device = Device(ctx.auth, ctx.host, ctx.port)
    status = vmanage_device.get_device_status(decommdevice, key='host-name')
    if 'uuid' in status:
        vmanage_device.put_device_decommission(status['uuid'])
    else:
        click.secho(f'Cannot find UUID for device {decommdevice}', fg="red")
